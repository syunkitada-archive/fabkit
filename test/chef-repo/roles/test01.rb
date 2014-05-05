name "test01"
description "test01 role applied to all nodes."

run_list "recipe[test1]"

override_attributes(
    "test" => {
        "hoge" => "piyo"
    }
)


