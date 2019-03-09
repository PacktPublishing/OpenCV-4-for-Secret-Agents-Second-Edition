using UnityEngine;
using UnityEngine.SceneManagement;

#if PLATFORM_ANDROID
using UnityEngine.Android;
#endif


public class Launcher : MonoBehaviour {

    void Start() {

#if PLATFORM_ANDROID
        if (!Permission.HasUserAuthorizedPermission(
                Permission.Camera))
        {
            // Ask the user's permission for camera access.
            Permission.RequestUserPermission(Permission.Camera);
        }
#endif

        SceneManager.LoadScene("Rollingball");
    }
}
