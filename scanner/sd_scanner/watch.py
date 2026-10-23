"""Cache vùng giá + vòng theo dõi ticker → Telegram khi cắt ngưỡng."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .config import Settings
from .episode import EpisodeState
from .exchange import MarketData
from .scoring import confidence_score, depth_score
from .telegram_notify import Telegram
from .zones import Zone, build_zones, price_in_zone


@dataclass
class ZoneCache:
    # symbol → tf → list[Zone]
    zones: dict[str, dict[str, list[Zone]]] = field(default_factory=dict)
    built_at: float = 0.0


class Watcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.market = MarketData()
        self.tg = Telegram(settings.telegram_token, settings.telegram_chat_id)
        self.cache = ZoneCache()
        self.episodes = EpisodeState()
        self.running = False

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

    def _aligned_count(self, symbol: str, side: str, price: float) -> int:
        n = 0
        for tf, zs in (self.cache.zones.get(symbol) or {}).items():
            for z in zs:
                if z.side == side and price_in_zone(price, z, pad_frac=0.02):
                    n += 1
                    break
        return n

    def check_once(self) -> int:
        """Một vòng ticker. Trả số tin đã gửi."""
        sent = 0
        for sym in self.settings.symbols:
            try:
                price = self.market.fetch_last(sym)
            except Exception as e:
                print(f"  ! giá {sym}: {e}")
                continue
            venue = self.market.venue_label(sym)
            for tf, zs in (self.cache.zones.get(sym) or {}).items():
                for z in zs:
                    band = self.episodes.on_price(sym, tf, z, price)
                    if band is None:
                        continue
                    conf_n = self._aligned_count(sym, z.side, price)
                    depth = depth_score(price, z)
                    conf = confidence_score(conf_n)
                    note = self._note(conf_n)
                    try:
                        self.tg.send_alert(
                            symbol=sym,
                            venue=venue,
                            timeframe=tf,
                            side=z.side,
                            price=price,
                            zone_bot=z.bot,
                            zone_top=z.top,
                            depth=depth,
                            confidence=conf,
                            note=note,
                        )
                        sent += 1
                        print(f"  → Noti {sym} {tf} {z.side} depth={depth} conf={conf}")
                    except Exception as e:
                        print(f"  ! Telegram: {e}")
            time.sleep(0.05)
        return sent

    @staticmethod
    def _note(n_tf: int) -> str:
        if n_tf <= 1:
            return "Chỉ 1 khung có vùng tại giá → độ tin cậy trung bình; mở chart tự kiểm tra."
        if n_tf == 2:
            return "2 khung đồng thuận vùng tại giá."
        return f"{n_tf} khung đồng thuận vùng tại giá."

    def start_watching(self) -> None:
        self.running = True
        print("Đang theo dõi… (Ctrl+C hoặc /stop trên Telegram để dừng)")
        self.tg.send(
            "✅ Đã bật theo dõi vùng giá.\n"
            f"Cặp: {', '.join(self.settings.symbols)}\n"
            f"Khung: {', '.join(self.settings.timeframes)}\n"
            f"Mỗi {self.settings.watch_interval_sec}s chỉ lấy giá; "
            "chỉ khi cắt ngưỡng mới báo.\n"
            "Lệnh: /status /stop"
        )
        last_rebuild = time.time()
        rebuild_every = 60 * 60  # 1 giờ rebuild vùng (nến HTF đổi chậm)
        while self.running:
            # lệnh Telegram
            for cmd in self.tg.poll_commands(timeout_sec=0):
                if cmd == "/stop":
                    self.running = False
                    self.tg.send("⏹ Đã dừng theo dõi. Bật lại bằng lệnh chạy scan trên máy hoặc /scan.")
                    break
                if cmd == "/status":
                    age = int(time.time() - self.cache.built_at)
                    self.tg.send(
                        f"📡 Đang chạy.\n"
                        f"Vùng cache tuổi: {age}s\n"
                        f"Cặp: {len(self.settings.symbols)}"
                    )
                if cmd == "/scan":
                    self.tg.send("🔄 Đang rebuild vùng giá…")
                    n = self.rebuild_zones()
                    self.tg.send(f"Xong rebuild: {n} vùng. Tiếp tục theo dõi.")
                    last_rebuild = time.time()
            if not self.running:
                break

            if time.time() - last_rebuild >= rebuild_every:
                print("Rebuild vùng định kỳ…")
                self.rebuild_zones()
                last_rebuild = time.time()

            sent = self.check_once()
            if sent:
                print(f"Vòng này gửi {sent} tin.")
            # vừa poll vừa chờ
            time.sleep(self.settings.watch_interval_sec)

    def run_scan_session(self) -> None:
        """Scan một lần (nạp vùng) rồi bật theo dõi đến khi dừng."""
        self.tg.send("🔎 Bắt đầu scan — đang tải vùng giá (Binance/Bybit)…")
        print("Rebuild zones…")
        n = self.rebuild_zones()
        self.tg.send(f"Scan xong: {n} vùng trên {len(self.settings.symbols)} cặp. Bật theo dõi.")
        # kiểm tra ngay 1 vòng (báo nếu đang trong vùng)
        self.check_once()
        self.start_watching()
