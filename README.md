An FTX crypto trading bot that uses React a frontend and Flask backend. The frontend is a UI that displays your current orders, and visualizes your net gain and loses as well as current crypto prices and an interface to make, customize, and cancel orders. The backend is calls the FTX API to make orders, cancel orders, and collect data from FTX. 

跑之前把 API, APIKEY 加進去。

In Backend Folder:

1. App.py 網頁
2. client_api_new 跟 FTX 溝通的 Class/功能
3. api_config.txt 現在網站用的 API, APIKEY,子帳號
4. orders.txt 從網站下的單
5. order.py 下單的 script
6. db_setup.py 建立新數據 structure（在 data 裡，前 100 天的利息數據，2400 小時）
7. db_update.py 每小時跟新數據的 script

前端是用 React 寫的。平常會跑"npm run build"後把 html,css,js 檔移到後段資料夾。
要跑前端的話要前後端都跑讓後去 localhost:3000。前端有 proxy 到 port 5000。

TODO:

- \_get, \_post, \_delete 的 Error Handling 因該可以加強。
- app.py API 路徑蠻亂的（前端的呼叫也要一起改）。
- config,orders 是用 txt 存的，歷史數據用 csv 存的。可進步。
- 前端的 code 基本上沒有刻意去 optimize 過。
