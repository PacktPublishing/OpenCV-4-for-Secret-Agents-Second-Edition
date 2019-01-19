package com.nummist.goldgesture;

public final class BackAndForthGesture {

    private double mMinDistance;

    private double mStartPosition;
    private double mDelta;

    private int mBackCount;
    private int mForthCount;

    public int getBackAndForthCount() {
        return Math.min(mBackCount, mForthCount);
    }

    public BackAndForthGesture(final double minDistance) {
        mMinDistance = minDistance;
    }

    public void start(final double position) {
        mStartPosition = position;
        mDelta = 0.0;
        mBackCount = 0;
        mForthCount = 0;
    }

    public void update(final double position) {
        double lastDelta = mDelta;
        mDelta = position - mStartPosition;
        if (lastDelta < mMinDistance &&
                mDelta >= mMinDistance) {
            mForthCount++;
        } else if (lastDelta > -mMinDistance &&
                mDelta < -mMinDistance) {
            mBackCount++;
        }
    }

    public void resetCounts() {
        mBackCount = 0;
        mForthCount = 0;
    }
}
