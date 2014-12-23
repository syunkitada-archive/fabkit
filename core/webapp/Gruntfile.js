module.exports = function(grunt) {

    grunt.initConfig({
        coffee: {
            build: {
                files: {
                    'static/js/common.js': [
                        'static_src/coffee/common/base.coffee',
                        'static_src/coffee/common/render.coffee',
                    ]
                }
            }
        },
        watch: {
            options: {
                interval: 1000
            },
            coffee: {
                files: ['static_src/coffee/**'],
                tasks: ['coffee'],
                options: {
                    livereload: true
                }
            },
            views: {
                files: [
                    'apps/**',
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
    grunt.registerTask('default', ['coffee', 'watch'])
};
