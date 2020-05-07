from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version
import os


class grpcConan(ConanFile):
    name = "grpc"
    version = "1.29.0"
    commit = "6340359197e88540ff2bb555d4af771688f9a4bd"
    description = "Google's RPC library and framework."
    topics = ("conan", "grpc", "rpc")
    url = "https://github.com/inexorgame/conan-grpc"
    homepage = "https://github.com/grpc/grpc"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake", "virtualrunenv"
    short_paths = True

    settings = "os", "arch", "compiler", "build_type"

    _cmake = None
	
    options = {
        # "shared": [True, False],
        "fPIC": [True, False],
        "build_codegen": [True, False],
        "build_csharp_ext": [True, False]
    }

    default_options = {
        "fPIC": True,
        "build_codegen": True,
        "build_csharp_ext": True
    }

    scm = {
        "type": "git",
        "url": "https://github.com/grpc/grpc.git",
        "subfolder": "source_subfolder",
        "revision": "v1.29.x",
        "recursive": True
     }

    _source_subfolder = "source_subfolder"

    build_requires = (
	    "protoc_installer/3.9.1@bincrafters/stable"
	)
    
    requires = (
        "zlib/1.2.11",
        #"openssl/1.1.1e",
        "protobuf/3.9.1@bincrafters/stable",
        "protoc_installer/3.9.1@bincrafters/stable",
        "c-ares/1.15.0",
        "abseil/20200205"
    )

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC
			
            compiler_version = tools.Version(self.settings.compiler.version)
			
            if compiler_version < 14:
                raise ConanInvalidConfiguration("gRPC can only be built with Visual Studio 2015 or higher.")
				
        self.options["protobuf"].shared = True
				
    def source(self):
        self.run("cd source_subfolder && git submodule update --init") 
        #tools.get(**self.conan_data["sources"][self.version])
        #extracted_dir = self.name + "-" + self.commit
        #os.rename("source", self._source_subfolder)

        #tools.rmdir("source_subfolder/examples")
        #tools.rmdir("source_subfolder/test_package")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
    
        #self._cmake.definitions['gRPC_BUILD_CODEGEN'] = "ON" if self.options.build_codegen else "OFF"
        #self._cmake.definitions['gRPC_BUILD_CSHARP_EXT'] = "ON" if self.options.build_csharp_ext else "OFF"
        #self._cmake.definitions['gRPC_BUILD_TESTS'] = "OFF"

        #self._cmake.definitions['protobuf_BUILD_EXAMPLES'] = "OFF"
        #self._cmake.definitions['protobuf_BUILD_TESTS'] = "OFF"

        # We need the generated cmake/ files (bc they depend on the list of targets, which is dynamic)
        #self._cmake.definitions['gRPC_INSTALL'] = "ON"
        # cmake.definitions['CMAKE_INSTALL_PREFIX'] = self._build_subfolder

        # tell grpc to use the find_package versions
        #self._cmake.definitions['gRPC_CARES_PROVIDER'] = "module"
        #self._cmake.definitions['gRPC_ZLIB_PROVIDER'] = "module"
        #self._cmake.definitions['gRPC_SSL_PROVIDER'] = "module"
        self._cmake.definitions['gRPC_PROTOBUF_PROVIDER'] = "package"
        #self._cmake.definitions['gRPC_BENCHMARK_PROVIDER'] = "none"

        # Compilation on minGW GCC requires to set _WIN32_WINNTT to at least 0x600
        # https://github.com/grpc/grpc/blob/109c570727c3089fef655edcdd0dd02cc5958010/include/grpc/impl/codegen/port_platform.h#L44
        #if self.settings.os == "Windows" and self.settings.compiler == "gcc":
        #    self._cmake.definitions["CMAKE_CXX_FLAGS"] = "-D_WIN32_WINNT=0x600"
        #    self._cmake.definitions["CMAKE_C_FLAGS"] = "-D_WIN32_WINNT=0x600"

        # cmake = CMake(self, toolset = f"{self.settings.compiler.toolset},host=x64")
        #self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.settings.os == "Windows":
            self.run("activate_run.bat && cmake build . -DCMAKE_BUILD_TYPE=Release -DgRPC_PROTOBUF_PROVIDER=package -DgRPC_ABSL_PROVIDER=package")
        else:
            self.run(". ./activate_run.sh && cmake . -DCMAKE_BUILD_TYPE=Release -DgRPC_PROTOBUF_PROVIDER=package -DgRPC_ABSL_PROVIDER=package && make -j4")

    def package(self):
        # cmake = self._configure_cmake()
        # cmake.install()

        self.copy(pattern="LICENSE", dst="licenses")
        self.copy('*', dst='include', src='{}/include'.format(self._source_subfolder))
        #self.copy('*.cmake', dst='lib', src='{}/lib'.format(), keep_path=True)
        self.copy("*.lib", dst="lib", src="", keep_path=False)
        self.copy("*.a", dst="lib", src="", keep_path=False)
        self.copy("*", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = [
            "grpc++_unsecure",
            "grpc++_reflection",
            "grpc++_error_details",
            "grpc++",
            "grpc_unsecure",
            "grpc_plugin_support",
            "grpc_cronet",
            "grpcpp_channelz",
            "grpc",
            "gpr",
            "address_sorting",
            "upb",
        ]

        if self.settings.compiler == "Visual Studio":
            self.cpp_info.system_libs += ["wsock32", "ws2_32"]
