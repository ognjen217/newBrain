# src/utils/ipManager/IpReplacement.py

class IPManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def replace_ip_in_file(self):
        try:
            with open(self.file_path, 'r') as file:
                content = file.read()
            # Primer: zamenjujemo "localhost" sa novom IP adresom (ovde "192.168.1.50")
            new_ip = "192.168.1.50"
            new_content = content.replace("localhost", new_ip)
            with open(self.file_path, 'w') as file:
                file.write(new_content)
            print(f"IP adresa zamenjena u {self.file_path}")
        except Exception as e:
            print("Greška pri zameni IP adrese:", e)

if __name__ == "__main__":
    manager = IPManager("web-socket.service.ts")
    manager.replace_ip_in_file()
