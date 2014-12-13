module.exports = function(grunt) {

    grunt.initConfig({
        watch: {
            options: {
                interval: 1000
            },
            views: {
                files: [
                    'home/**',
                    'node/**',
                    'templates/**',
                    'static/**',
                ],
                options: {
                    livereload: true,
                }
            }
        }
    });

    // パッケージの自動読み込み
    var pkg = grunt.file.readJSON('package.json');
    var taskName;
    for (taskName in pkg.devDependencies) {
        if (taskName.substring(0, 6) == 'grunt-') {
            grunt.loadNpmTasks(taskName);
        }
    }

    // grunt.registerTask('default', ['cssmin', 'watch'])
    grunt.registerTask('default', ['watch'])
};
