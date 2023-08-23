"""Create config file for the project."""
import markdown

PORT = 80
DEBUG = False
AUTO_RELOAD = True

# SOCIAL MEDIA LINK :)
SOCIAL_MEDIA = {
  "telegram": "https://s.id/1LRRU",  # False or url to your telegram
  "facebook": "https://s.id/1LRqw",  # False or url to your facebook
  "instagram": "https://s.id/1LRS0",  # False or url to your instagram
  "github": "https://s.id/1LRSf",  # False or url to your github
}

APP_TITLE = "API"
APP_DESCRIPTION = "API ini dibuat untuk mempermudah dalam mengambil data dari website."

AUTHOR_NAME = "Xnuvers007"
AUTHOR_NAME2 = "IhsanDevs"
AUTHOR_LINK = "https://github.com/Xnuvers007"
AUTHOR_LINK2 = "https://github.com/IhsanDevs"

CHANGELOG = [
  "Cek Openai APIKEY", "Cek Jadwal Pertandingan Bola [15/08/2023]",
  "ZeroGPT-1 (pengecek apakah kalimat tersebut dibuat oleh AI atau tidak) [19/07/2023]",
  "ZeroGPT-2 (versi ke 2 dari ZeroGPT-1 [20/07/2023]",
  "Update fix bug pada fitur API bola/sepakbola [15/08/2023]",
  "Youtube Playlist dan cari video [25/07/2023]",
  "Cek kerentanan website clickjacking [26/07/2023]",
  "Cek Parafrase kalimat [28/07/2023]",
  "Lupa Youtube Search (rilis bareng dengan playlist)",
  "penambahan fitur Facebook Downloader [15/08/2023]"
]

GALERIES = [
  {
    "image": "https://i.ibb.co/gMptW7w/1.webp",
    "link": {
      "href": "https://gtmetrix.com/reports/tr.deployers.repl.co/3PiRf2GP/",
      "text": "Lihat Hasil GTMetrix DESKTOP",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/ydbyBhV/2.webp",
    "link": {
      "href":
      "https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=mobile",
      "text": "Lihat Hasil PageSpeed Insights MOBILE",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/8d26vYv/4.webp",
    "link": {
      "href":
      "https://pagespeed.web.dev/analysis/https-tr-deployers-repl-co/ekypysxvaa?form_factor=desktop",
      "text": "Lihat Hasil PageSpeed Insights DESKTOP",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/bv4RtJZ/3.webp",
    "link": {
      "href": "https://www.debugbear.com/test/website-speed/aVgrP5ip/overview",
      "text": "Lihat Hasil DebugBear MOBILE",
    },
    "description": False,
  },
  {
    "image": "https://i.ibb.co/7jT5r76/5.webp",
    "link": {
      "href": "https://www.debugbear.com/test/website-speed/oPoks49H/overview",
      "text": "Lihat Hasil DebugBear DESKTOP",
    },
    "description": False,
  },
  {
    "image":
    "https://i.ibb.co/Jt96t7N/7.webp",
    "link": {
      "href":
      "https://jupyter.xnuvers007.repl.co/notebooks/tr.deployers.repl.co.ipynb",
      "text": "Lihat hasil Jupyter (password = xnuvers007), tekan see more",
    },
    "description":
    markdown.markdown("""
        import requests

        url = "https://tr.deployers.repl.co"

        while True:
            response = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.162 Mobile Safari/537.36"})
            response2 = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0"})

            print("Android: ",response.elapsed.total_seconds())
            print("Desktop: ",response2.elapsed.total_seconds())"""),
  },
]

API_SERVICES = [{
  "name":
  "Blood Pressure",
  "description":
  "Parameter untuk tekanan darah sistolik dan diastolik, serta denyut jantung.",
  "parameters": [
    {
      "name": "tensi",
      "type": "integer",
      "required": True
    },
    {
      "name": "hb",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/bp?tensi=125&hb=91",
}, {
  "name": "Bola",
  "description": "API Website untuk melihat jadwal pertandingan Bola.",
  "url": "/jadwal-pertandingan",
}, {
  "name":
  "Checker APIKEY Openai (ChatGPT)",
  "description":
  "Melakukan Pengecekan Pada APIKEY Openai (data apikey tidak disimpan).",
  "parameters": [
    {
      "name": "key",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/openai?key=YOUR_APIKEY",
}, {
  "name":
  "Clickjacking/Clickjacker",
  "description":
  "Melakukan pengecekan Kerentanan / Kelemahan pada suatu website dengan metode pemeriksaan clickjacking.",
  "parameters": [{
    "name": "u",
    "type": "string",
    "required": True
  }],
  "url":
  "/cj?u=",
}, {
  "name":
  "Convert Uang",
  "description":
  "Pengkonversi Uang. Masukkan paramter yang ingin di konversi.",
  "parameters": [
    {
      "name": "uang",
      "type": "integer",
      "required": True
    },
    {
      "name": "dari",
      "type": "string",
      "required": True
    },
    {
      "name": "ke",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/convertuang?uang=1&dari=usd&ke=idr",
},{
  "name": "Facebook Downloader",
  "description": "Parameter untuk mendownload Video dari platform yang bernama Facebook.",
  "parameters": [{
    "name": "u",
    "type": "string",
    "required": True
  }],
  "url": "/fb?u=LINKKAMU"
},{
  "name":
  "Google News Indonesia",
  "description":
  "Parameter untuk jumlah berita yang ingin ditampilkan.",
  "parameters": [
    {
      "name": "berita",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/indonesia?berita=5",
}, {
  "name":
  "Google News World",
  "description":
  "Parameter untuk jumlah berita yang ingin ditampilkan.",
  "parameters": [
    {
      "name": "news",
      "type": "integer",
      "required": True
    },
  ],
  "url":
  "/world?news=5",
}, {
  "name":
  "Google Translate",
  "description":
  "Parameter untuk teks yang ingin diterjemahkan, bahasa asal, dan bahasa tujuan.",
  "parameters": [
    {
      "name": "dari",
      "type": "string",
      "required": True
    },
    {
      "name": "ke",
      "type": "string",
      "required": True
    },
    {
      "name": "text",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/translate?from=en&to=id&text=hello,%20im%20Xnuvers007,%20Im%20the%20developer",
}, {
  "name":
  "Instagram Stalk",
  "description":
  "Parameter untuk username Instagram yang ingin di-stalk.",
  "parameters": [
    {
      "name": "user",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/igstalk?user=Indradwi.25",
}, {
  "name":
  "Jam",
  "description":
  "Parameter untuk wilayah atau lokasi yang ingin diperoleh informasi waktu.",
  "parameters": [
    {
      "name": "wilayah",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/jam?wilayah=jakarta",
}, {
  "name":
  "Kamus",
  "description":
  "Penerjemah kata. Masukkan text yang ingin diterjemahkan",
  "parameters": [
    {
      "name": "text",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/kamus?text=sleep",
}, {
  "name":
  "Keterangan Obat",
  "description":
  "Parameter untuk nama obat yang ingin diperoleh keterangannya",
  "parameters": [
    {
      "name": "obat",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/keterangan?obat=/obat-dan-vitamin/flunarizine-10-mg-20-tablet/",
}, {
  "name":
  "Nama Kanji",
  "description":
  "Parameter untuk nama yang ingin diterjemahkan.",
  "parameters": [
    {
      "name": "nama",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/kanjiname?nama=Jokowi%20Widodo",
}, {
  "name":
  "Obat Halodoc",
  "description":
  "Parameter untuk nama obat/nama penyakit yang ingin dicari untuk obatnya",
  "parameters": [
    {
      "name": "obat",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/cariobat?obat=pusing",
}, {
  "name":
  "Parafrase Checker",
  "description":
  "Parameter Untuk melakukan parafrase pada sebuah kalimat agar bertujuan mudah dipahami dan tidak memperboros kata",
  "parameters": [{
    "name": "teks",
    "type": "string",
    "required": True
  }, {
    "name": "mode",
    "type": "string",
    "required": True
  }],
  "url":
  "/parafrase?teks=&mode="
}, {
  "name":
  "Short URL",
  "description":
  "Parameter untuk memperpendek URL/Link yang sangat panjang",
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/short?url=github.com/xnuvers007",
}, {
  "name":
  "Tiktok Downloader",
  "description":
  "Parameter untuk mendownload video di Tiktok",
  "parameters": [
    {
      "name": "url",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/tiktok?url=https://www.tiktok.com/@yurii_kun5/video/7225627953185721627?is_from_webapp=1"
}, {
  "name":
  "Youtube Playlist",
  "description":
  "melakukan pencarian video berdasarkan playlist youtube yang ada",
  "parameters": [{
    "name": "name",
    "type": "string",
    "required": True
  }, {
    "name": "lim",
    "type": "integer",
    "required": True
  }],
  "url":
  "/playlist?name=Kanao Tsuyuri&lim=15"
},{
  "name":
  "Youtube Search",
  "description":
  "melakukan pencarian video berdasarkan pencarian youtube yang anda cari",
  "parameters": [{
    "name": "name",
    "type": "string",
    "required": True
  }, {
    "name": "lim",
    "type": "integer",
    "required": True
  }],
  "url":
  "/vid?name=Kanao Tsuyuri&lim=15"
}, {
  "name": "ZeroGPT-1",
  "description":
  "Alat/AI pengecek apakah kata tersebut terbuat dari AI atau tidak",
  "url": "/zerogpt"
}, {
  "name":
  "ZeroGPT-2",
  "description":
  "Alat/AI ke 2 dari ZeroGPT-1, pengecek apakah kata tersebut dibuat oleh AI atau tidak",
  "parameters": [
    {
      "name": "t",
      "type": "string",
      "required": True
    },
  ],
  "url":
  "/zerogptjson?t=MASUKAN+TEKSNYA+DISINI"
}]
