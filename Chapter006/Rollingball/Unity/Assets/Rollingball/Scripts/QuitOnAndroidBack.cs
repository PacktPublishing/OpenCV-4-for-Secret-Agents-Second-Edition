using UnityEngine;


namespace com.nummist.rollingball {

    public sealed class QuitOnAndroidBack : MonoBehaviour {

        void Start() {
            // Show the standard Android navigation bar.
            Screen.fullScreen = false;
        }

        void Update() {
            if (Input.GetKeyUp(KeyCode.Escape)) {
                Application.Quit();
            }
        }
    }
}
