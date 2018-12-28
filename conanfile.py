import os
from conans import ConanFile, CMake, tools
from conans.util import files


class FlatBuffersConan(ConanFile):
    version = "1.10.0"
    
    name = "flatbuffers"
    license = "https://github.com/google/flatbuffers/blob/master/LICENSE.txt"
    description = "FlatBuffers is an efficient cross platform serialization library for games and other memory constrained apps. It allows you to directly access serialized data without unpacking/parsing it first, while still having great forwards/backwards compatibility."
    url = "https://github.com/ulricheck/conan-flatbuffers"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    # The folder name when the *.tar.gz release is extracted
    folder_name = "flatbuffers-%s" % version
    # The name of the archive that is downloaded from Github
    archive_name = "%s.tar.gz" % folder_name
    # The temporary build diirectory
    build_dir = "./%s/buildpkg" % folder_name

    def source(self):
        tools.download(
            "https://github.com/google/flatbuffers/archive/v%s.tar.gz" % self.version,
            self.archive_name
        )
        tools.unzip(self.archive_name)
        os.unlink(self.archive_name)

    def build(self):
        files.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake = CMake(self)
            cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = "OFF"
            cmake.definitions["FLATBUFFERS_INSTALL"] = "OFF"
            if self.options.shared:
                cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = "OFF"
                cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = "ON"
                if tools.os_info.is_macos:
                    cmake.definitions["CMAKE_MACOSX_RPATH"] = "ON"
            else:
                cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = "ON"
                cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = "OFF"

            cmake.configure(source_dir="..", build_dir=".")
            cmake.build(build_dir=".")
            os.rename("../LICENSE.txt", "../LICENSE.FlatBuffers")

    def package(self):
        self.copy("flatc", dst="bin",
                  src=self.build_dir, keep_path=False)
        self.copy("flathash", dst="bin",
                  src=self.build_dir, keep_path=False)
        self.copy("*.exe", dst="bin",
                  src=self.build_dir, keep_path=False)
        self.copy("*.h", dst="include/flatbuffers",
                  src="%s/include/flatbuffers" % self.folder_name)
        self.copy("*.lib", dst="lib",
                  src=self.build_dir, keep_path=False)
        self.copy("*.dll", dst="bin",
                  src=self.build_dir, keep_path=False)
        self.copy("*.a", dst="lib",
                  src=self.build_dir, keep_path=False)
        self.copy("*.so*", dst="lib",
                  src=self.build_dir, keep_path=False)
        self.copy("*.dylib*", dst="lib",
                  src=self.build_dir, keep_path=False)
        self.copy("LICENSE.FlatBuffers", src=self.folder_name)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
