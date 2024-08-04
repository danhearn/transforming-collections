from pythonosc import udp_client as udp

class SemanticClient: 
    def __init__(self, ip, port):
        self.client = udp.SimpleUDPClient(ip, port)
        
    def send_vectors(self, message ,vectors):
        self.client.send_message(message, vectors)

