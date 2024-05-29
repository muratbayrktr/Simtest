from _base_socket import Client
import json 

class BaseStrategy(Client):
    def __init__(self):
        super().__init__()

    def on_disconnect(self):
        """
        Summary: This method is called when the strategy disconnects to the server.
                Signals Backtester to stop sending data.
        Args:   
            None

        Returns:
            None
        """
        pass
        
    def on_connect(self):
        """
        Summary: This method is called when the strategy connects to the server.
                Signals Backtester to start sending data.
        Args:   
            None

        Returns:
            None
        """
        # Send start signal to get the data stream
        payload = {'message': 'START'}
        self.send(payload)

    def on_receive(self, data: json) :
        """
        Summary: This method is called when the strategy receives data from the server.

        Args:
            data: can be price, signal, or any other data sent from the server.

            This function should send orders to the server using the send method.
            For example:

                self.send(OpenLong(self.id, None, close_price, self.position_size).to_dict())
            
            if you are not going to place any order you should send a NoOrder object:
            
                self.send(NoOrder())
        """
        pass
            
        


