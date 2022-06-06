# Kstat

部内SNSのBOTの情報取得部分


## 動作例

<img width="546" alt="dousa" src="https://user-images.githubusercontent.com/43299846/172115346-09bfd3cb-984f-48a6-bdd4-739ba0f4efba.png">

## 仕組み

 部内サーバーが弱いため、部内サーバーのリソースを大量に消費することは好ましくない。
 そこで、部内サーバーにはSNS上でトリガーとなるワードが発されたときに、イベントを発火するだけにして、リソース消費を最小限に抑えている。
 Herokuに立ててあるサーバー上でリソースを要する作業を行えるようにしている。
