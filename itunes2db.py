import os
import sqlite3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.mp4 import MP4


# 音楽ファイルのハフルパスを取得
def get_music_files(folder_path):
    music_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.mp3') or file.endswith('.m4a'):
                full_path = os.path.join(root, file)
                music_files.append(full_path)
    return music_files

# Windowsのユーザー名を取得
windows_username = os.getlogin()

# 対象フォルダルートパス
music_folder_path_root = 'C:\\Users\\' + windows_username + '\\Music\\iTunes\\iTunes Media\\Music'

# 音楽データを格納するリスト
music_files_list = get_music_files(music_folder_path_root)

# メタデータを格納するリスト
metadata_list = []

# 音楽データ（mp3, m4a）のメタデータ値を取得
for file_path in music_files_list:
    title, artist, album, track_number = 'Unknown title', 'Unknown artist', 'Unknown album', 'Unknown track'  # Default values

    if file_path.endswith('.mp3'):
        audio = MP3(file_path, ID3=ID3)
        title_obj = audio.get('TIT2', 'Unknown title')
        artist_obj = audio.get('TPE1', 'Unknown artist')
        album_obj = audio.get('TALB', 'Unknown album')
        track_number_obj = audio.get('TRCK', 'Unknown track')

        title = title_obj.text[0] if hasattr(title_obj, 'text') else title_obj
        artist = artist_obj.text[0] if hasattr(artist_obj, 'text') else artist_obj
        album = album_obj.text[0] if hasattr(album_obj, 'text') else album_obj
        track_number = track_number_obj.text[0] if hasattr(track_number_obj, 'text') else track_number_obj
        
    elif file_path.endswith('.m4a'):
        audio = MP4(file_path)
        title = audio.get('\xa9nam', ['Unknown title'])[0]
        artist = audio.get('\xa9ART', ['Unknown artist'])[0]
        album = audio.get('\xa9alb', ['Unknown album'])[0]
        track_number = audio.get('trkn', [(0, 0)])[0][0]
        
    metadata_list.append((title, artist, album, track_number))

# SQLiteデータベースの作成と接続
conn = sqlite3.connect('iTunesMusic.db')
c = conn.cursor()

# テーブル作成
c.execute('''
CREATE TABLE IF NOT EXISTS music (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    album TEXT,
    track_number TEXT
);
''')

# メタデータの挿入（重複チェック付き）
for metadata in metadata_list:
    title, artist, album, track_number = metadata

    # 重複チェック
    c.execute("SELECT * FROM music WHERE title = ? AND artist = ? AND album = ? AND track_number = ?",
              (title, artist, album, track_number))
    
    if c.fetchone() is None:
        c.execute("INSERT INTO music (title, artist, album, track_number) VALUES (?, ?, ?, ?)", 
                  (title, artist, album, track_number))

# コミットとクローズ
conn.commit()
conn.close()

print("Done!")