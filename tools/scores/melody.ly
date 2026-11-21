\include "common.ily"
% 第7章《窓辺》8小節。4/4、四分＝84。本文の表、assets/examples.js、window-melody.musicxml と同じ音。
\score {
  <<
    \new ChordNames \chordmode {
      c1 f1 d1:m7 g1:7 c1 f1 d2:m7 g2:7 c1
    }
    \new Staff \relative c' {
      \set Score.currentBarNumber = #1
      \bar ""
      \clef treble \time 4/4 \tempo 4 = 84
      c4 d e g | a g f2 | e4 f8 g a4 g | f4 d g2 | \break
      c,4 d e g | c a g f | e f d b' | c2 g4 c, \bar "|."
    }
  >>
  \layout { }
}
