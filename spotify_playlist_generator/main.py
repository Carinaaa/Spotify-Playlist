from scrap_billboard import BillboardScrap
from connect_spotify import SpotifyPlaylistCreator

if __name__ == "__main__":

    bill = BillboardScrap()
    bill.write_non_relational_db()

    data = bill.get_data()

    spc = SpotifyPlaylistCreator()
    spc.populate_playlist(data)

