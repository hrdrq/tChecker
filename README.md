# 古本販売可能チェッカー

台湾の古本代理代理販売サイトは在庫により書籍の販売を制限されている。

毎日に書籍が販売できるか調査するワーカーを作った

## 機能
AWS LambdaとCloudWatchを使い、

毎朝にデータベースに保存されているISBNデータを

代理販売サイトのAPI経由で販売できるかをチェックする

## 注意事項
該当APIはログインが必要で、reCAPTCHA使っているので、

PILを使って、画像から数字を抽出する必要がある

tesseract-lambda.zipをfunctions/checkに解凍

aws lambdaのEnvironment variablesにTESSDATA_PREFIX　：　/var/task　を設定

PILのlinux版を使用