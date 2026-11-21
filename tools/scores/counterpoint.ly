\include "common.ily"
% 第13章の第1種対位法。上声（緑）と定旋律（青）を一つの五線に書く。
\score {
  \new Staff \with {
    \remove "Time_signature_engraver"
  } <<
    \set Score.currentBarNumber = #1
    \clef treble \time 4/4
    \new Voice { \voiceOne \override NoteHead.color = \upper
      \bar "" g'1 | f' | g' | a' | g' | b' | c'' \bar "|." }
    \new Voice { \voiceTwo \override NoteHead.color = \lower
      c'1 | d' | e' | f' | e' | d' | c' }
  >>
  \layout { }
}
