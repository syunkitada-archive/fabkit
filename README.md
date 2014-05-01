# chefric

fabfile for chef

いろいろと未完成

## TODO
* chef-serverとの連携, chef-serverのprepare
* cookbookのfabric版
* proxy複数切り替えられるようにする(nodeごとで使いたいproxy違うかも)

## 利用条件
* chefがインストールされている
* knife soloがインストールされている
* fabricがインストールされている
* chef-repoの直下にこのfabfileを置いて使用
* chef-serverはオプションで利用

## 初期設定
``` bash
# chef-repo直下で以下を実行してください
$ git clone git@github.com:syunkitada/chefric.git fabfile

# fab commandが実行できたら成功です
$ fab -l
Available commands:

    cook
    node
    prepare
    role
    test
```

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

