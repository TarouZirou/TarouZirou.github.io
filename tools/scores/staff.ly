\include "common.ily"
% 第1章の譜例：ト音記号の五線上で C4、D4、E4、G4、C5 を読む
\paper { line-width = 110\mm }
\score {
  <<
    \new Staff \with {
      \remove "Time_signature_engraver"
      \remove "Bar_engraver"
    } { \clef treble \cadenzaOn c'4 s4 d'4 s4 e'4 s4 g'4 s4 c''4 }
    \addlyrics { "C4" "D4" "E4" "G4" "C5" }
  >>
  \layout {
    \context { \Lyrics \override LyricText.font-size = #-1 }
    \context { \Score \remove "Bar_number_engraver" }
  }
}
