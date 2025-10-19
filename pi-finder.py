from mpmath import mp
import time
import threading
import sys

class FastPiFinder:
    def __init__(self):
        self.chunk_size = 1_000_000
        mp.dps = self.chunk_size
        self.digits_searched = 0
        self.running = False
        self.start_time = None

    def progress_display(self):
        """Sürekli güncellenen ilerleme göstergesi"""
        last_digits = 0
        while self.running:
            if self.start_time is not None:
                elapsed = time.time() - self.start_time
                speed = self.digits_searched / elapsed if elapsed > 0 else 0
                digits_since_last = self.digits_searched - last_digits
                
                # Satırı temizle ve güncelle
                sys.stdout.write('\r' + ' ' * 100 + '\r')  # Satırı temizle
                sys.stdout.write(
                    f"🔍 {self.digits_searched:,} basamak | "
                    f"Hız: {speed:,.0f} basamak/sn | "
                    f"Son hız: {digits_since_last:,} basamak/sn"
                )
                sys.stdout.flush()
                
                last_digits = self.digits_searched
            time.sleep(1)  # 1 saniye bekle

    def find_number(self, search_number):
        self.digits_searched = 0
        current_position = 0
        self.running = True
        self.start_time = time.time()

        # İlerleme gösterici thread'ini başlat
        progress_thread = threading.Thread(target=self.progress_display)
        progress_thread.daemon = True
        progress_thread.start()

        print("\nArama başladı... (Ctrl+C ile durdurmak için)\n")

        try:
            while True:
                mp.dps = current_position + self.chunk_size
                pi_chunk = str(mp.pi)[2:][current_position:current_position + self.chunk_size]
                
                position = pi_chunk.find(str(search_number))
                self.digits_searched += len(pi_chunk)

                if position != -1:
                    self.running = False
                    absolute_position = current_position + position + 1
                    context_start = max(0, position - 10)
                    context = f"...{pi_chunk[context_start:position]}{search_number}{pi_chunk[position+len(str(search_number)):position+len(str(search_number))+10]}..."
                    
                    # Son satırı temizle
                    sys.stdout.write('\r' + ' ' * 100 + '\r')
                    sys.stdout.flush()
                    
                    return {
                        "found": True,
                        "position": absolute_position,
                        "context": context,
                        "digits_searched": self.digits_searched,
                        "time_taken": time.time() - self.start_time
                    }

                current_position += self.chunk_size - len(str(search_number))

        except KeyboardInterrupt:
            self.running = False
            # Son satırı temizle
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            sys.stdout.flush()
            
            return {
                "found": False,
                "digits_searched": self.digits_searched,
                "time_taken": time.time() - self.start_time,
                "stopped_by_user": True
            }

    def get_pi_range(self, start_pos, end_pos):
        if end_pos - start_pos > 1_000_000:
            print("⚠️ Uyarı: Büyük aralıklar biraz zaman alabilir.")
        
        try:
            mp.dps = end_pos + 10
            pi_str = str(mp.pi)[2:]
            result = pi_str[start_pos-1:end_pos]
            return result
        except Exception as e:
            print(f"Hata oluştu: {e}")
            return None

def main():
    print("🚀 Gerçek Zamanlı Pi Sayısı Bulucu v3.0 🔍")
    print("----------------------------------------")
    
    finder = FastPiFinder()
    
    while True:
        print("\nNe yapmak istersiniz?")
        print("1. İki basamak arası Pi sayılarını bul")
        print("2. Sayı ara")
        print("3. Çıkış")
        
        choice = input("\nSeçiminiz (1-3): ")
        
        if choice == "3":
            break
            
        elif choice == "1":
            try:
                start = int(input("Başlangıç basamağı: "))
                end = int(input("Bitiş basamağı: "))
                
                if start < 1 or end < start:
                    print("❌ Geçersiz aralık! Başlangıç 1'den büyük ve bitiş başlangıçtan büyük olmalı.")
                    continue
                
                print("\n🔄 İşleniyor...")
                start_time = time.time()
                
                result = finder.get_pi_range(start, end)
                if result:
                    print(f"\n✨ {start}. ve {end}. basamaklar arası Pi sayıları:")
                    print(f"📝 Sayılar: {result}")
                    print(f"📏 Uzunluk: {len(result)} basamak")
                    print(f"⏱️ Süre: {time.time() - start_time:.2f} saniye")
                
            except ValueError:
                print("❌ Lütfen geçerli sayılar girin!")
                
        elif choice == "2":
            number = input("Aramak istediğiniz sayıyı girin: ")
            
            if not number.isdigit():
                print("❌ Lütfen geçerli bir sayı girin!")
                continue
                
            result = finder.find_number(number)
            
            if result["found"]:
                print(f"\n✨ {number} sayısı Pi'de bulundu!")
                print(f"📍 Pozisyon: {result['position']:,}. basamak")
                print(f"📝 Bağlam: {result['context']}")
                print(f"🔍 Toplam aranan basamak: {result['digits_searched']:,}")
                print(f"⏱️ Toplam arama süresi: {result['time_taken']:.2f} saniye")
                print(f"🚀 Ortalama hız: {result['digits_searched']/result['time_taken']:,.0f} basamak/saniye")
            else:
                if result.get("stopped_by_user"):
                    print(f"\n⛔ Arama kullanıcı tarafından durduruldu")
                    print(f"🔍 Toplam aranan basamak: {result['digits_searched']:,}")
                    print(f"⏱️ Geçen süre: {result['time_taken']:.2f} saniye")
                    print(f"🚀 Ortalama hız: {result['digits_searched']/result['time_taken']:,.0f} basamak/saniye")
                else:
                    print(f"\n❌ {number} bulunamadı")

if __name__ == "__main__":
    main()