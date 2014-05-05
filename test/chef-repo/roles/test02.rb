name 'test02'
description 'test02 role applied to all nodes.'

run_list 'role[test01]',
         'recipe[test2]'

override_attributes(
    'test' => {
        'hoge' => 'piyo'
    }
)
