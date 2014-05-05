# chefric

This is fabfile of fabric for chef.

いろいろと未完成

## 開発目的
* rubyよりもpythonが好き！
* chef-serverを使いたくない
 * サーバの運用をしたくない
 * データベースとか使わずに、すべてファイルにしてGitで管理したい
* knife soloがちょっと使いづらい
 * ノード一個づつのセットアップなら良いが、ノードをまとめてセットアップできない  
 * chefricは、正規表現（みたいなの）でノードを選択し、並列でchef-solo実行する


## Docs
* [Getting Started](https://github.com/syunkitada/chefric/blob/master/docs/GETTING_STARTED.md)
* [Tutorial](https://github.com/syunkitada/chefric/blob/master/docs/TUTORIAL.md)
* [TODO](https://github.com/syunkitada/chefric/blob/master/docs/TODO.md)

## 使い方
### ホスト名の指定について
タスク利用時にホスト名を指定する場合があります。  
その際に、[]を利用すると以下のように展開して処理されます。
```
test[1-3]
> test1, test2, test3

test[2+4]
> test2, test4

test[1-3+5-7]
> test1, test2, test3, test5, test6, test7

test[1-2]host[4+7]
> test1host4, test1host7, test2host4, test2host7
```


### nodeタスク
nodeの登録、nodeの閲覧、nodeの編集、nodeの削除が行えます。
また、続くタスクのセットアップ対象のnodeを設定します。
``` bash
# nodeの閲覧
$ fab node:[host_pattern]

# nodeの登録
$ fab node:create[,host_pattern]
enter hostname: [host_pattern]

# nodeの削除
$ fab node:remove[,host_pattern]
enter hostname: [host_pattern]

# nodeの編集
$ fab node:edit[,host_pattern,edit_target,edit_value]
enter hostname: [host_pattern]
enter edit target: [target]

# chefサーバへnodeのアップロード
$ fab node:upload[,host_pattern]
enter hostname: [host_pattern]

# chefサーバからnodeのダウンロード
$ fab node:download[,host_pattern]
enter hostname: [host_pattern]
```

### roleタスク
roleの閲覧のみ行えます。  
roleファイルの編集はサポートしません。
``` bash
$ fab role:[reguler exception]
```


### prepareタスク
セットアップ対象のnodeに、chefをインストールします。  
必ず、hostタスクの後に実行してください。
``` bash
$ fab host:[host_pattern] prepare
```


### cookタスク
セットアップ対象のnodeで、chef-soloを実行します。  
必ず、hostタスクの後に実行してください。
``` bash
$ fab host:[host_pattern] cook
```

### checkタスク
セットアップ対象のnodeの検証をします。  
ping, ssh, uptimeを取得します。
``` bash
$ fab host:[host_pattern] cook
```

### testタスク
各タスクのテストを行うためのタスクです。  
タスクの修正を行った場合は、これを実行してエラーが出ないことを確認して下さい。  
新規タスクを開発する場合は、そのテストコードをtest/\__init__.pyに登録してください。
``` bash
$ fab test
...
Ran 15 tests in 0.291s

OK

Done.
```

## タスクの追加
ユーザの独自のタスクを追加して利用できます。
### 利用方法
chef-repo直下にfabscriptフォルダを作成し、ここにタスクスクリプトを作成します。
``` bash
# 例
$ cd chef-repo
$ mkdir fabscript

# __init__.pyでタスクのモジュールを登録する
$ vim fabscript/__init__.py
import helloworld

# タスクの定義
$ vim fabscript/helloworld.py
from fabric.api import env, task
from api import *
import util, conf

@task
def hello():
    host_json = util.load_json()
    print host_json

    cmd('hostname')
    local('hostname')
    run('hostname')
    sudo('hostname')

# 実行
$ fab node:* helloworld.hello
```

### sys.path
以下のパス配下のモジュールは自由に呼ぶことができます
* chef-repo
* fabfile(chefric)
* fabfile(chefric)/lib

