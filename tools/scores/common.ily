% 本書の楽譜の共通設定。
% 符頭の高さは五線の線間（1スペース）ちょうど。LilyPond の標準の符頭をそのまま使い、
% 拡大・縮小する場合も譜表ごと（staff size）で変えて、符頭と線間の比を崩さない。
\version "2.24.0"
#(set-global-staff-size 26)
\paper {
  indent = 0
  line-width = 150\mm
  tagline = ##f
  print-page-number = ##f
  oddHeaderMarkup = ##f
  evenHeaderMarkup = ##f
  oddFooterMarkup = ##f
  evenFooterMarkup = ##f
}
\header { tagline = ##f }
ink = #(rgb-color 0.13 0.20 0.18)      % 本文の文字色 #22342d に近い色
upper = #(rgb-color 0.15 0.36 0.29)    % 緑 #255d4a
lower = #(rgb-color 0.18 0.37 0.53)    % 青 #2f5f86
% 本文が小節番号で説明するので、すべての小節に番号を出す
\layout {
  \context {
    \Score
    barNumberVisibility = #all-bar-numbers-visible
    \override BarNumber.break-visibility = ##(#f #t #t)
    \override BarNumber.font-size = #-2
    \override BarNumber.self-alignment-X = #RIGHT
    \override BarNumber.color = #(rgb-color 0.45 0.52 0.48)
  }
}
