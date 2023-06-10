library(ggplot2) # グラフ描画用

# コンフィグ
xmin <- 1 # 描画する最初の実行回数(xmin回目から)
xmax <- 1000000 # 描画する最後の実行回数(xma回目まで)


# 1)CSVを読み込む
barabara <- read.table(file = "result_barabara.csv", header = TRUE, sep = ",")
kotei <- read.table(file = "result_kotei.csv", header = TRUE, sep = ",")


# 2)グラフ表示用のデータに加工
try_range <- seq(xmin, xmax) # 実行回数の範囲
target_data <- data.frame(
  # バラバラのデータを並べた後に固定のデータを結合する。

  # グラフの色分け用の設定(戦略別で色を変える)
  storagagy = rep(c("バラバラ", "固定"), each = (xmax - xmin + 1)),

  # x軸(実行回数)のデータ。バラバラ、固定のデータを結合。
  try = c(barabara$total[try_range], kotei$total[try_range]),

  # y軸(確率)のデータ。バラバラ、固定のデータを結合。
  per = c(barabara$percentage[try_range], kotei$percentage[try_range])
)


# 3)グラフ描画設定
# 3-1)データの基本設定：x軸を実行回数、y軸を確率、戦略で色を変える
graph <- ggplot(target_data, aes(x = try, y = per, color = storagagy))

# 3-2)グラフ種類：折れ線グラフ
graph <- graph + geom_line()

# 3-3)x軸の設定：対数軸(log10)、目盛(1,10,100...)、補助線と余白を消す
max_break <- trunc(log10(xmax)) # 目盛の最大：常用対数(切り捨て)
graph <- graph + scale_x_log10(breaks = 10^(0:max_break), labels = 10^(0:max_break), minor_breaks = NULL, expand = c(0, 0))

# 3-4)y軸の設定：余白を少し付ける
graph <- graph + scale_y_continuous(expand = c(0, 0.5))

# 3-5)log用の目盛設定：下(x軸のみ)
graph <- graph + annotation_logticks(sides = "b")

# 3-6)ラベルの設定
graph <- graph + labs(title = "音楽神経衰弱のシミュレーション結果") # タイトル
graph <- graph + xlab("実行回数[回]") # x軸のラベル
graph <- graph + ylab("確率[%]") # y軸のラベル
graph <- graph + labs(color = "戦略") # 凡例

# 3-7)テーマ(見た目)の設定
graph <- graph + theme_bw()


# 4)グラフを描画して保存
plot(graph)
ggsave(filename = "graph.png", device = "png", dpi = "retina", scale = 1.0, width = 16, height = 9)
