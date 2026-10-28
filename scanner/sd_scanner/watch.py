"""Cache vùng giá + vòng theo dõi ticker → Telegram khi cắt ngưỡng."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import Settings
from .episode import EpisodeState
from .exchange import MarketData
from .levels import next_target, risk_reward, stop_level, take_profit_price
from .scoring import confidence_score, depth_score
from .telegram_notify import Telegram
from .watchlist_store import save_symbols
from .zones import Zone, build_zones, price_in_zone


@dataclass
class ZoneCache:
    # symbol → tf → list[Zone]
    zones: dict[str, dict[str, list[Zone]]] = field(default_factory=dict)
    built_at: float = 0.0


@dataclass
class PendingAdd:
    options: list[dict[str, str]]  # symbol, venue, label
    created_at: float


class Watcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.market = MarketData()
        self.tg = Telegram(settings.telegram_token, settings.telegram_chat_id)
        self.cache = ZoneCache()
        q = settings.quality
        self.episodes = EpisodeState(
            cooldown_sec=q.cooldown_sec,
            side_cooldown_sec=q.side_cooldown_sec,
            min_band=q.min_depth_band,
        )
        self.running = False
        self.pending_add: PendingAdd | None = None

    def rebuild_zones(self) -> int:
        """Tải nến + dựng vùng. Trả tổng số vùng."""
        self.market.warmup(self.settings.symbols)
        total = 0
        new_map: dict[str, dict[str, list[Zone]]] = {}
        for sym in self.settings.symbols:
            new_map[sym] = {}
            for tf in self.settings.timeframes:
                try:
                    df = self.market.fetch_ohlcv(sym, tf, self.settings.zone.lookback_bars)
                    zs = build_zones(df, self.settings.zone)
                    new_map[sym][tf] = zs
                    total += len(zs)
                    print(f"  {sym} {tf}: {len(zs)} vùng")
                except Exception as e:
                    print(f"  ! {sym} {tf}: {e}")
                    new_map[sym][tf] = []
                time.sleep(0.15)
        self.cache.zones = new_map
        self.cache.built_at = time.time()
        return total

    def rebuild_one(self, symbol: str) -> int:
        total = 0
        self.cache.zones.setdefault(symbol, {})
        for tf in self.settings.timeframes:
            try:
                df = self.market.fetch_ohlcv(symbol, tf, self.settings.zone.lookback_bars)
                zs = build_zones(df, self.settings.zone)
                self.cache.zones[symbol][tf] = zs
                total += len(zs)
                print(f"  {symbol} {tf}: {len(zs)} vùng")
            except Exception as e:
                print(f"  ! {symbol} {tf}: {e}")
                self.cache.zones[symbol][tf] = []
            time.sleep(0.15)
        self.cache.built_at = time.time()
        return total

    def _aligned_count(self, symbol: str, side: str, price: float) -> int:
        n = 0
        for _tf, zs in (self.cache.zones.get(symbol) or {}).items():
            for z in zs:
                if z.side == side and price_in_zone(price, z, pad_frac=0.0):
                    n += 1
                    break
        return n

    def check_once(self) -> int:
        """Một vòng ticker. Trả số tin đã gửi (đã lọc chất lượng)."""
        sent = 0
        q = self.settings.quality
        alert_tfs = set(q.alert_timeframes)
        for sym in self.settings.symbols:
            try:
                price = self.market.fetch_last(sym)
            except Exception as e:
                print(f"  ! giá {sym}: {e}")
                continue
            for tf, zs in (self.cache.zones.get(sym) or {}).items():
                for z in zs:
                    # H1 (và TF khác ngoài list): chỉ cập nhật trạng thái, không bắn tin
                    if tf not in alert_tfs:
                        self.episodes.on_price(sym, tf, z, price, emit=False)
                        continue

                    conf_n = self._aligned_count(sym, z.side, price)
                    depth = depth_score(price, z)
                    quality_ok = depth >= q.min_depth_score and conf_n >= q.min_aligned_tfs
                    band = self.episodes.on_price(sym, tf, z, price, emit=quality_ok)
                    if band is None:
                        continue

                    conf = confidence_score(conf_n)
                    stl = stop_level(z.side, z)
                    tgt = next_target(z.side, price, zs)
                    tp = take_profit_price(z.side, tgt) if tgt is not None else None
                    rr = risk_reward(price, stl, tp)
                    try:
                        self.tg.send_alert(
                            symbol=sym,
                            timeframe=tf,
                            side=z.side,
                            price=price,
                            zone_bot=z.bot,
                            zone_top=z.top,
                            stl=stl,
                            tp=tp,
                            rr=rr,
                            depth=depth,
                            confidence=conf,
                        )
                        sent += 1
                        print(
                            f"  → Noti {sym} {tf} {z.side} "
                            f"stl={stl} tp={tp} rr={rr} depth={depth} conf={conf}"
                        )
                    except Exception as e:
                        print(f"  ! Telegram: {e}")
            time.sleep(0.05)
        return sent

    def _commit_add(self, chosen: dict[str, str]) -> None:
        """Lưu ticker đã chọn vào watchlist + tải vùng."""
        sym = chosen["symbol"]
        if sym in self.settings.symbols:
            self.tg.send(f"{sym} đã có trong danh sách rồi.")
            return
        try:
            self.market.resolve(sym)
        except Exception as e:
            self.tg.send(f"❌ Không dùng được {sym}: {e}")
            return

        self.settings.symbols.append(sym)
        try:
            save_symbols(self.settings.watchlist_path, self.settings.symbols)
        except Exception as e:
            self.tg.send(f"❌ Lưu watchlist lỗi: {e}")
            self.settings.symbols.remove(sym)
            return

        self.tg.send(f"✅ Đã thêm {sym} ({chosen['venue']}).\nĐang tải vùng giá cặp này…")
        try:
            n = self.rebuild_one(sym)
            self.tg.send(
                f"Xong. {sym}: {n} vùng.\n"
                f"Danh sách hiện tại ({len(self.settings.symbols)}): "
                + ", ".join(self.settings.symbols)
            )
        except Exception as e:
            self.tg.send(f"Đã lưu {sym} nhưng tải vùng lỗi: {e}. Thử /scan.")

    def _handle_add_query(self, query: str) -> None:
        self.tg.send(f"🔎 Đang tìm «{query}» trên Binance Perp (không có thì Bybit)…")
        try:
            opts = self.market.search_perp_tickers(query, limit=10)
        except Exception as e:
            self.tg.send(f"❌ Lỗi tìm ticker: {e}")
            return
        if not opts:
            self.tg.send(
                f"Không thấy perp USDT khớp «{query}» trên Binance/Bybit.\n"
                "Thử tên khác (vd. LIT, PEPE, 1000PEPE)."
            )
            self.pending_add = None
            return
        # Chỉ 1 kết quả → thêm luôn, không hỏi chọn số
        if len(opts) == 1:
            self.pending_add = None
            self.tg.send(f"Chỉ thấy 1 ticker: {opts[0]['label']} → thêm luôn.")
            self._commit_add(opts[0])
            return
        self.pending_add = PendingAdd(options=opts, created_at=time.time())
        lines = ["Chọn số ticker cần thêm:", ""]
        for i, o in enumerate(opts, start=1):
            lines.append(f"{i}. {o['label']}")
        lines += ["", "Gõ số (vd. 1). Gõ /cancel để hủy."]
        self.tg.send("\n".join(lines))

    def _handle_add_choice(self, text: str) -> bool:
        """True nếu đã xử lý (kể cả lỗi chọn)."""
        if self.pending_add is None:
            return False
        if time.time() - self.pending_add.created_at > 300:
            self.pending_add = None
            self.tg.send("Hết thời gian chọn ticker. Gõ /add … lại.")
            return True
        if not text.isdigit():
            self.tg.send("Đang chờ bạn chọn số (1, 2, 3…). Gõ /cancel để hủy.")
            return True
        idx = int(text)
        opts = self.pending_add.options
        if idx < 1 or idx > len(opts):
            self.tg.send(f"Chỉ chọn từ 1 đến {len(opts)}.")
            return True
        chosen = opts[idx - 1]
        self.pending_add = None
        self._commit_add(chosen)
        return True

    def _dispatch_message(self, text: str) -> None:
        raw = text.strip()
        # đang chờ chọn số?
        if self.pending_add is not None and not raw.startswith("/"):
            self._handle_add_choice(raw)
            return

        if not raw.startswith("/"):
            return

        parts = raw.split()
        cmd = parts[0].split("@")[0].lower()

        if cmd == "/cancel":
            self.pending_add = None
            self.tg.send("Đã hủy /add.")
            return

        if cmd == "/add":
            if len(parts) < 2:
                self.tg.send("Cú pháp: /add TÊN\nVí dụ: /add LIT  hoặc  /add PEPE")
                return
            query = " ".join(parts[1:])
            self._handle_add_query(query)
            return

        if cmd == "/list":
            self.tg.send("📋 Cặp đang theo dõi:\n" + "\n".join(f"• {s}" for s in self.settings.symbols))
            return

        if cmd == "/stop":
            self.running = False
            self.pending_add = None
            self.tg.send("⏹ Đã dừng theo dõi. Bật lại bằng lệnh scan trên máy.")
            return

        if cmd == "/status":
            age = int(time.time() - self.cache.built_at) if self.cache.built_at else 0
            pend = " (đang chờ chọn ticker /add)" if self.pending_add else ""
            self.tg.send(
                f"📡 Đang chạy{pend}.\n"
                f"Vùng cache tuổi: {age}s\n"
                f"Cặp ({len(self.settings.symbols)}): "
                + ", ".join(self.settings.symbols)
            )
            return

        if cmd == "/scan":
            self.tg.send("🔄 Đang rebuild vùng giá…")
            n = self.rebuild_zones()
            self.tg.send(f"Xong rebuild: {n} vùng. Tiếp tục theo dõi.")
            return

        if cmd == "/help":
            self.tg.send(
                "Lệnh:\n"
                "/add TÊN — tìm & thêm cặp (vd. /add LIT)\n"
                "/list — xem danh sách\n"
                "/scan — tải lại vùng\n"
                "/status — trạng thái\n"
                "/stop — dừng\n"
                "/cancel — hủy bước chọn ticker"
            )

    def start_watching(self) -> None:
        self.running = True
        print("Đang theo dõi… (Ctrl+C hoặc /stop trên Telegram để dừng)")
        q = self.settings.quality
        self.tg.send(
            "✅ Đã bật theo dõi (chế độ ít nhiễu).\n"
            f"Cặp: {', '.join(self.settings.symbols)}\n"
            f"Khung báo tin: {', '.join(q.alert_timeframes)} "
            f"(cần ≥{q.min_aligned_tfs} TF + độ sâu ≥{q.min_depth_score})\n"
            f"Mỗi {self.settings.watch_interval_sec}s lấy giá; "
            "chỉ khi đủ chất lượng mới báo.\n"
            "Lệnh: /add /list /status /scan /stop /help"
        )
        last_rebuild = time.time()
        rebuild_every = 60 * 60
        while self.running:
            for msg in self.tg.poll_messages(timeout_sec=0):
                try:
                    self._dispatch_message(msg)
                except Exception as e:
                    print(f"  ! lệnh TG: {e}")
                    try:
                        self.tg.send(f"Lỗi xử lý lệnh: {e}")
                    except Exception:
                        pass
                if not self.running:
                    break
            if not self.running:
                break

            # khi đang chờ chọn số /add — poll nhanh hơn, chưa check giá
            if self.pending_add is not None:
                time.sleep(1)
                continue

            if time.time() - last_rebuild >= rebuild_every:
                print("Rebuild vùng định kỳ…")
                self.rebuild_zones()
                last_rebuild = time.time()

            sent = self.check_once()
            if sent:
                print(f"Vòng này gửi {sent} tin.")
            # poll xen kẽ trong lúc chờ interval
            end = time.time() + self.settings.watch_interval_sec
            while time.time() < end and self.running:
                for msg in self.tg.poll_messages(timeout_sec=0):
                    self._dispatch_message(msg)
                if self.pending_add is not None:
                    break
                time.sleep(1)

    def run_scan_session(self) -> None:
        """Scan một lần (nạp vùng) rồi bật theo dõi đến khi dừng."""
        self.tg.send("🔎 Bắt đầu scan — đang tải vùng giá (Binance/Bybit)…")
        print("Rebuild zones…")
        n = self.rebuild_zones()
        self.tg.send(f"Scan xong: {n} vùng trên {len(self.settings.symbols)} cặp. Bật theo dõi.")
        self.check_once()
        self.start_watching()
