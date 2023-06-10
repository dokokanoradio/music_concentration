# music_concentration
音楽神経衰弱のシミュレーション用ファイルです。<br>
シミュレーション用のpythonスクリプトとグラフ描画用のRスクリプトから構成されます。

# 事前準備
* Windows11で動作確認しています。
* 凝ったことをしているわけではないので、他のOSでも動くとは思います。

## 1)最低限必要なもののインストール
* Python 3
  * [Python公式](https://www.python.org/downloads/)から各OS向けのファイルがDL可能です。
  * Windwos(x64)のVer.3.11.4で動作確認しています。
* R
  * [R公式](https://cran.r-project.org/mirrors.html) から(ミラー経由で各OS向けのファイルがDL可能です。
    * 例えば日本のミラーだと https://ftp.yz.yamagata-u.ac.jp/pub/cran/
  * Windows版の4.3.0で動作確認しています。

## 2)[Option]あれば便利なものをインストール
* RStudio
  * [RStudio公式](https://posit.co/download/rstudio-desktop/)からDL可能です。
  * Windows版の2023.06.0で動作確認しています。

## 3)ggplot2(R用のグラフライブラリ)をインストール
* グラフはggplot2を利用して描画しています。
* Rを起動し、プロンプトで`install.packages("ggplot2")`を実行すればインストール可能。

# 取りあえず動かしてみる
1. コマンドプロンプトなどで`python main.py`を実行してCSVを生成する。
2. RないしはRStudio上でgraph.Rを読み込んで実行する。<br>
   (事前にワーキングディレクトリをgraph.Rがあるディレクトリに設定すること)
3. graph.pngが出来上がる。

# 実行結果のサンプル
* sampleフォルダ内に格納しています。
![グラフのイメージ](/sample/graph.png)

# 参考：ファイルの内容
## main.py
* 選択をバラバラにした場合と固定した場合での正解確率を計算するpythonスクリプトです。
* コマンドプロンプトなどででmain.pyにあるフォルダに移動し、引数無しで`python main.py`でOKです。(Windowsの場合は`py.exe main.py`)
* 定数のGAMESを変更することで、シミュレーションするゲーム数を変更できます。
* シミュレーション結果はそれぞれCSVファイルで出力されます。
  * バラバラはデフォルトだと"result_barabara.csv"で保存
  * 固定はデフォルトだと"result_kotei.csv"で保存
* [TIPS]ファイル名を変更したい場合はCSV_BARA, CSV_KOTEIを変更すればOK
* 出力ファイルのイメージはsampleフォルダ内を参照してください。

## graph.R
* main.pyで生成した結果を折れ線グラフで表示するRスクリプトです。
* 事前にgraph.RとCSVファイルが同じディレクトリにあり、ワーキングディレクトリ設定済みであることを確認してください。
* 描画範囲はスクリプト内のxmin,xmaxを調整することで変更できます。
* ファイルはgraph.pngとして保存されます。
