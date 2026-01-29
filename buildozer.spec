[app]

# (str) Title of your application
title = Mon Budget

# (str) Package name
package.name = monbudget

# (str) Package domain (needed for android/ios packaging)
package.domain = org.nathmn14

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json,db

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to exclude nothing)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to exclude nothing)
source.exclude_dirs = tests, bin, venv, env, .git, .idea

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,README.md

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,kivymd==1.2.0,pillow,requests,urllib3,charset-normalizer,idna,certifi,plyer,sqlite3

# (str) Custom source folders for requirements
# packageless_directories = utils,data,models,controllers,views

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 23b

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess downloads or network problems
#android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when installing or updating
# the SDK.
android.accept_sdk_license = True

# (str) Android entry point, default is PythonActivity
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for KivyMD
android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the single apk build
#android.whitelist =

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (requires API >= 23)
android.allow_backup = True

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jar files that you do not need, since each jar
# add time to the build process.
#android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) List of Java files to add to the android project (can be python within
# a .jar, or java source files)
#android.add_src =

# (list) Android AAR archives to add (currently only works with sdl2_gradle
# bootstrap)
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) add java compile options to gradle (e.g. --target 1.8)
#android.add_compile_options = "--source 1.8", "--target 1.8"

# (list) Python modules to add (for example, names of modules that should be compiled)
#android.add_python_modules =

# (list) Java classes to add (names of classes that should be compiled)
#android.add_java_classes =

# (list) add java external libraries (e.g. jars)
#android.add_java_libs =

# (list) add java external libraries (e.g. aar)
#android.add_java_aars =

# (list) add java external libraries (e.g. maven)
#android.add_java_maven_repositories =

# (list) add java external libraries (e.g. maven)
#android.add_java_maven_dependencies =

# (list) add java external libraries (e.g. custom repositories)
#android.add_java_custom_repositories =

# (list) add java external libraries (e.g. custom dependencies)
#android.add_java_custom_dependencies =

# (list) add java external libraries (e.g. custom sources)
#android.add_java_custom_sources =

# (list) add java external libraries (e.g. custom assets)
#android.add_java_custom_assets =

# (list) add java external libraries (e.g. custom res)
#android.add_java_custom_res =

# (list) add java external libraries (e.g. custom jni)
#android.add_java_custom_jni =

# (list) add java external libraries (e.g. custom manifest)
#android.add_java_custom_manifest =

# (list) add java external libraries (e.g. custom gradle)
#android.add_java_custom_gradle =

# (list) add java external libraries (e.g. custom gradle dependencies)
#android.add_java_custom_gradle_dependencies =

# (list) add java external libraries (e.g. custom gradle repositories)
#android.add_java_custom_gradle_repositories =

# (list) add java external libraries (e.g. custom gradle tasks)
#android.add_java_custom_gradle_tasks =

# (list) add java external libraries (e.g. custom gradle projects)
#android.add_java_custom_gradle_projects =

# (list) add java external libraries (e.g. custom gradle subprojects)
#android.add_java_custom_gradle_subprojects =

# (list) add java external libraries (e.g. custom gradle buildscript)
#android.add_java_custom_gradle_buildscript =

# (list) add java external libraries (e.g. custom gradle settings)
#android.add_java_custom_gradle_settings =

# (list) add java external libraries (e.g. custom gradle properties)
#android.add_java_custom_gradle_properties =

# (list) add java external libraries (e.g. custom gradle init)
#android.add_java_custom_gradle_init =

# (list) add java external libraries (e.g. custom gradle wrapper)
#android.add_java_custom_gradle_wrapper =

# (list) add java external libraries (e.g. custom gradle gradlew)
#android.add_java_custom_gradle_gradlew =

# (list) add java external libraries (e.g. custom gradle bat)
#android.add_java_custom_gradle_bat =

# (list) add java external libraries (e.g. custom gradle jar)
#android.add_java_custom_gradle_jar =

# (list) add java external libraries (e.g. custom gradle aar)
#android.add_java_custom_gradle_aar =

# (list) add java external libraries (e.g. custom gradle zip)
#android.add_java_custom_gradle_zip =

# (list) add java external libraries (e.g. custom gradle tar)
#android.add_java_custom_gradle_tar =

# (list) add java external libraries (e.g. custom gradle war)
#android.add_java_custom_gradle_war =

# (list) add java external libraries (e.g. custom gradle ear)
#android.add_java_custom_gradle_ear =

# (list) add java external libraries (e.g. custom gradle sources)
#android.add_java_custom_gradle_sources =

# (list) add java external libraries (e.g. custom gradle javadoc)
#android.add_java_custom_gradle_javadoc =

# (list) add java external libraries (e.g. custom gradle groovydoc)
#android.add_java_custom_gradle_groovydoc =

# (list) add java external libraries (e.g. custom gradle poms)
#android.add_java_custom_gradle_poms =

# (list) add java external libraries (e.g. custom gradle ivy)
#android.add_java_custom_gradle_ivy =

# (list) add java external libraries (e.g. custom gradle publication)
#android.add_java_custom_gradle_publication =

# (list) add java external libraries (e.g. custom gradle component)
#android.add_java_custom_gradle_component =

# (list) add java external libraries (e.g. custom gradle artifact)
#android.add_java_custom_gradle_artifact =

# (list) add java external libraries (e.g. custom gradle configuration)
#android.add_java_custom_gradle_configuration =

# (list) add java external libraries (e.g. custom gradle dependency)
#android.add_java_custom_gradle_dependency =

# (list) add java external libraries (e.g. custom gradle repository)
#android.add_java_custom_gradle_repository =

# (list) add java external libraries (e.g. custom gradle project)
#android.add_java_custom_gradle_project =

# (list) add java external libraries (e.g. custom gradle plugin)
#android.add_java_custom_gradle_plugin =

# (list) add java external libraries (e.g. custom gradle extension)
#android.add_java_custom_gradle_extension =

# (list) add java external libraries (e.g. custom gradle convention)
#android.add_java_custom_gradle_convention =

# (list) add java external libraries (e.g. custom gradle extra)
#android.add_java_custom_gradle_extra =

# (list) add java external libraries (e.g. custom gradle logger)
#android.add_java_custom_gradle_logger =

# (list) add java external libraries (e.g. custom gradle logging)
#android.add_java_custom_gradle_logging =

# (list) add java external libraries (e.g. custom gradle logback)
#android.add_java_custom_gradle_logback =

# (list) add java external libraries (e.g. custom gradle log4j)
#android.add_java_custom_gradle_log4j =

# (list) add java external libraries (e.g. custom gradle slf4j)
#android.add_java_custom_gradle_slf4j =

# (list) add java external libraries (e.g. custom gradle commons)
#android.add_java_custom_gradle_commons =

# (list) add java external libraries (e.g. custom gradle google)
#android.add_java_custom_gradle_google =

# (list) add java external libraries (e.g. custom gradle android)
#android.add_java_custom_gradle_android =

# (list) add java external libraries (e.g. custom gradle buildscript)
#android.add_java_custom_gradle_buildscript =

# (list) add java external libraries (e.g. custom gradle all)
#android.add_java_custom_gradle_all =

# (list) add java external libraries (e.g. custom gradle everything)
#android.add_java_custom_gradle_everything =

# (bool) use gradle instead of ant
android.gradle_dependencies = 'androidx.core:core:1.8.0', 'androidx.appcompat:appcompat:1.4.2'

[buildozer]

# (int) log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
