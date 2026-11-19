'use strict';

const melody = [
  [[60,1],[62,1],[64,1],[67,1]], [[69,1],[67,1],[65,2]],
  [[64,1],[65,.5],[67,.5],[69,1],[67,1]], [[65,1],[62,1],[67,2]],
  [[60,1],[62,1],[64,1],[67,1]], [[72,1],[69,1],[67,1],[65,1]],
  [[64,1],[65,1],[62,1],[71,1]], [[72,2],[67,1],[60,1]]
];
const harmony = [[0,48,64,67],[4,41,60,65,69],[8,50,60,65,69],[12,43,59,62,65],
                 [16,48,64,67],[20,41,60,65,69],[24,50,60,65,69],[26,43,59,62,65],[28,48,64,67]];
const upper = [67,65,67,69,67,71,72];
const lower = [60,62,64,65,64,62,60];
const status = document.querySelector('#player-status');
let context;
let track;
let request = 0;

function silence() {
  if (!track) return;
  const old = track;
  track = undefined;
  const t = context.currentTime;
  old.master.gain.setTargetAtTime(0, t, .012);
  for (const oscillator of old.oscillators) oscillator.stop(t + .05);
}

async function play(kind) {
  const ticket = ++request;
  silence();
  if (!context) context = new AudioContext();
  await context.resume();
  if (ticket !== request) return;
  const master = context.createGain();
  master.gain.value = .09;
  master.connect(context.destination);
  const current = {master, oscillators:[]};
  track = current;
  const start = context.currentTime + .075;
  const beat = kind === 'counterpoint' ? .46 : 60/84;
  let lastOscillator;

  function note(pitch, time, beats, gain, tone) {
    const osc = context.createOscillator();
    const envelope = context.createGain();
    const onset = start + time * beat;
    const end = onset + beats * beat;
    osc.type = tone;
    osc.frequency.value = 440 * 2 ** ((pitch-69)/12);
    envelope.gain.setValueAtTime(0, onset);
    envelope.gain.linearRampToValueAtTime(gain, onset+.019);
    envelope.gain.setValueAtTime(gain*.82, end-.05);
    envelope.gain.linearRampToValueAtTime(0, end);
    osc.connect(envelope).connect(master);
    osc.onended = () => { osc.disconnect(); envelope.disconnect(); };
    osc.start(onset);
    osc.stop(end+.004);
    current.oscillators.push(osc);
    lastOscillator = osc;
  }

  if (kind === 'counterpoint') {
    upper.forEach((p, i) => note(p, i*4, 3.88, .31, 'triangle'));
    lower.forEach((p, i) => note(p, i*4, 3.88, .24, 'sine'));
  } else {
    if (kind === 'arranged') harmony.forEach(([begin, bass, ...chord], i) => {
      const duration = (harmony[i+1]?.[0] ?? 32) - begin;
      note(bass, begin, duration-.065, .23, 'sine');
      chord.forEach(p => note(p, begin, duration-.065, .07, 'sine'));
    });
    melody.forEach((bar,i) => {
      let at=i*4;
      for (const [pitch, duration] of bar) {
        note(pitch, at, duration-.045, .40, 'triangle');
        at += duration;
      }
    });
  }
  const oldHandler = lastOscillator.onended;
  lastOscillator.onended = () => {
    oldHandler();
    master.disconnect();
    if (track === current) {
      track = undefined;
      status.textContent = '再生が終わりました。';
    }
  };
  const names = {counterpoint:'二声対位法', arranged:'《窓辺》和声付き', melody:'《窓辺》旋律のみ'};
  status.textContent = names[kind]+'を再生中';
}

for (const button of document.querySelectorAll('[data-play]')) {
  button.addEventListener('click', () => {
    const kind=button.dataset.play;
    if (kind==='stop') {
      request++;
      silence();
      status.textContent='停止しました。';
    } else {
      play(kind).catch(() => { status.textContent = '再生を開始できませんでした。Web Audio対応ブラウザで開いてください。'; });
    }
  });
}

