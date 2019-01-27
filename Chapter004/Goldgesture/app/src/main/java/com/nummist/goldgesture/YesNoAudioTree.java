package com.nummist.goldgesture;

import android.content.Context;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;

public final class YesNoAudioTree {

    private enum Affiliation { UNKNOWN, MI6, CIA, KGB, CRIMINAL }

    private int mLastAudioResource;
    private Affiliation mAffiliation;

    private Context mContext;
    private MediaPlayer mMediaPlayer;

    public YesNoAudioTree(final Context context) {
        mContext = context;
    }

    public void start() {
        mAffiliation = Affiliation.UNKNOWN;
        play(R.raw.intro);
    }

    public void stop() {
        if (mMediaPlayer != null) {
            mMediaPlayer.release();
        }
    }

    public void takeYesBranch() {

        if (mMediaPlayer != null && mMediaPlayer.isPlaying()) {
            // Do not interrupt the audio that is already playing.
            return;
        }

        switch (mAffiliation) {
            case UNKNOWN:
                switch (mLastAudioResource) {
                    case R.raw.q_mi6:
                        mAffiliation = Affiliation.MI6;
                        play(R.raw.q_martinis);
                        break;
                    case R.raw.q_cia:
                        mAffiliation = Affiliation.CIA;
                        play(R.raw.q_bond_friend);
                        break;
                    case R.raw.q_kgb:
                        mAffiliation = Affiliation.KGB;
                        play(R.raw.q_chief);
                        break;
                    case R.raw.q_criminal:
                        mAffiliation = Affiliation.CRIMINAL;
                        play(R.raw.q_chief);
                        break;
                }
                break;
            case MI6:
                // The person works for MI6.
                switch (mLastAudioResource) {
                    case R.raw.q_martinis:
                        // The person drinks shaken martinis (007).
                        play(R.raw.win_007);
                        break;
                    case R.raw.q_abbreviate:
                        // The person's name is abbreviated to one letter.
                        // Ask whether the person is the chief (M).
                        play(R.raw.q_chief);
                        break;
                    case R.raw.q_chief:
                        // The person is the chief (M).
                        play(R.raw.win_m);
                        break;
                    case R.raw.q_secretary:
                        // The person is the secretary (Miss Moneypenny).
                        play(R.raw.win_moneypenny);
                        break;
                    case R.raw.q_bond_friend:
                        // The person is Bond's friend (Bill Tanner).
                        play(R.raw.win_tanner);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case CIA:
                // The person works for the CIA.
                switch (mLastAudioResource) {
                    case R.raw.q_bond_friend:
                        // The person is Bond's friend (Felix Leiter).
                        play(R.raw.win_leiter);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case KGB:
                // The person works for the KGB.
                switch (mLastAudioResource) {
                    case R.raw.q_chief:
                        // The person is the chief (General Gogol).
                        play(R.raw.win_gogol);
                        break;
                    case R.raw.q_secretary:
                        // The person is the secretary (Miss Rublevitch).
                        play(R.raw.win_rublevitch);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case CRIMINAL:
                // The person works for a criminal organization.
                switch (mLastAudioResource) {
                    case R.raw.q_chief:
                        // The person is the chief.
                        // Ask whether the person has an Angora cat.
                        play(R.raw.q_angora);
                        break;
                    case R.raw.q_angora:
                        // The person has an Angora cat.
                        // The person must be Ernst Stavro Blofeld.
                        play(R.raw.win_blofeld);
                        break;
                    case R.raw.q_dentures:
                        // The person has steel dentures (Jaws).
                        play(R.raw.win_jaws);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
        }
    }

    public void takeNoBranch() {

        if (mMediaPlayer != null && mMediaPlayer.isPlaying()) {
            // Do not interrupt the audio that is already playing.
            return;
        }

        switch (mAffiliation) {
            case UNKNOWN:
                switch (mLastAudioResource) {
                    case R.raw.q_mi6:
                        // The person does not work for MI6.
                        // Ask whether the person works for a criminal
                        // organization.
                        play(R.raw.q_criminal);
                        break;
                    case R.raw.q_kgb:
                        // The person does not work for the KGB.
                        // Ask whether the person work for the CIA.
                        play(R.raw.q_cia);
                        break;
                    case R.raw.q_criminal:
                        // The person does not work for a criminal
                        // organization.
                        // Ask whether the person works for the KGB.
                        play(R.raw.q_kgb);
                        break;
                    case R.raw.q_cia:
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case MI6:
                // The person works for MI6.
                switch (mLastAudioResource) {
                    case R.raw.q_martinis:
                        // The person does not drink shaken martinis (007).
                        // Ask whether the person's name is abbreviated to
                        // one letter (M or Q).
                        play(R.raw.q_abbreviate);
                        break;
                    case R.raw.q_abbreviate:
                        // The person's name is not abbreviated to one
                        // letter (M or Q).
                        // Ask whether the person is the secretary (Miss
                        // Moneypenny).
                        play(R.raw.q_secretary);
                        break;
                    case R.raw.q_chief:
                        // The person's name is abbreviated to one letter (M
                        // or Q) but the person is not the chief (M).
                        // The person must be Q.
                        play(R.raw.win_q);
                        break;
                    case R.raw.q_secretary:
                        // The person is not the secretary (Miss
                        // Moneypenny).
                        // Ask whether the person is Bond's friend (Bill
                        // Tanner).
                        play(R.raw.q_bond_friend);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case CIA:
                // The person works for the CIA.
                switch (mLastAudioResource) {
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case KGB:
                // The person works for the KGB.
                switch (mLastAudioResource) {
                    case R.raw.q_chief:
                        // The person is not the chief (General Gogol).
                        // Ask whether the person is the secretary (Miss
                        // Rublevitch).
                        play(R.raw.q_secretary);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
            case CRIMINAL:
                // The person works for a criminal organization.
                switch (mLastAudioResource) {
                    case R.raw.q_chief:
                        // The person is not the chief.
                        // Ask whether the person has steel dentures.
                        play(R.raw.q_dentures);
                        break;
                    default:
                        // The person remains unknown.
                        play(R.raw.lose);
                        break;
                }
                break;
        }
    }

    private void takeAutoBranch() {
        switch (mLastAudioResource) {
            case R.raw.intro:
                play(R.raw.q_mi6);
                break;
            case R.raw.win_007:
            case R.raw.win_blofeld:
            case R.raw.win_gogol:
            case R.raw.win_jaws:
            case R.raw.win_leiter:
            case R.raw.win_m:
            case R.raw.win_moneypenny:
            case R.raw.win_q:
            case R.raw.win_rublevitch:
            case R.raw.win_tanner:
            case R.raw.lose:
                start();
                break;
        }
    }

    private void play(final int audioResource) {
        mLastAudioResource = audioResource;
        mMediaPlayer = MediaPlayer.create(mContext, audioResource);
        mMediaPlayer.setOnCompletionListener(
                new OnCompletionListener() {
                    @Override
                    public void onCompletion(
                            final MediaPlayer mediaPlayer) {
                        mediaPlayer.release();
                        if (mMediaPlayer == mediaPlayer) {
                            mMediaPlayer = null;
                        }
                        takeAutoBranch();
                    }
                });
        mMediaPlayer.start();
    }
}
