#!/bin/bash
cd ~;

apt install -y default-jdk;

echo "export JAVA_HOME=/usr/lib/jvm/default-java"  >>  ~/.profile;

wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz;

tar -xf hadoop-3.3.4.tar.gz -C /usr/local/;

echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> ~/.profile;
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile;

source ~/.profile;

echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh;
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh;

head -n -3 $HADOOP_HOME/etc/hadoop/core-site.xml > tmp.txt && mv tmp.txt $HADOOP_HOME/etc/hadoop/core-site.xml;
head -n -4 $HADOOP_HOME/etc/hadoop/hdfs-site.xml > tmp.txt && mv tmp.txt $HADOOP_HOME/etc/hadoop/hdfs-site.xml;


echo "<configuration><property><name>hadoop.tmp.dir</name><value>/var/lib/hadoop</value></property></configuration>" >> $HADOOP_HOME/etc/hadoop/core-site.xml;
echo "<configuration><property><name>dfs.replication</name><value>1</value></property></configuration>" >> $HADOOP_HOME/etc/hadoop/hdfs-site.xml

apt install -y ssh;

service ssh restart;

ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa;
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys;
chmod 0600 ~/.ssh/authorized_keys;

mkdir /var/lib/hadoop;
chmod 777 /var/lib/hadoop;

hdfs namenode -format;
touch ~/start;
echo "export HDFS_NAMENODE_USER=\"root\""  >>  ~/.profile;
echo "export HDFS_DATANODE_USER=\"root\""  >>  ~/.profile;
echo "export HDFS_SECONDARYNAMENODE_USER=\"root\""  >>  ~/.profile;
echo "export YARN_RESOURCEMANAGER_USER=\"root\""  >>  ~/.profile;
echo "export YARN_NODEMANAGER_USER=\"root\""  >>  ~/.profile;

source ~/.profile;

$HADOOP_HOME/sbin/start-dfs.sh;


hdfs dfs -mkdir -p input;

apt install git -y;

git clone https://github.com/miboz/files.git;

hadoop com.sun.tools.javac.Main files/WordCount.java;

cd files;

jar cf wc.jar WordCount*.class;

hadoop fs -cp ~/files/pg4300.txt ~/input;

cd ~;

# Save wordcount execution time of Ulysses dataset using Hadoop
echo "Hadoop - Ulysses" >> time_results.txt
{ time hadoop jar files/wc.jar WordCount ./input/ ./output; } 2>> time_results.txt

# Save wordcount execution time of Ulysses dataset using Linux
echo "Linux - Ulysses" >> time_results.txt
{ time cat files/pg4300.txt | tr ' ' '\n' | sort | uniq -c; } 2>> time_results.txt 

# spark dependencies configuration
apt-get update;
cd ~;
apt install python3-pip -y;
pip install pyspark;
pip install findspark;

# Loop dataset folder and save wordcount execution time for each dataset using spark
for file in $(ls datasets/) 
do
    # remove file extension
    filename=$(echo $file| cut  -d'.' -f 1);
    echo $filename >> time_results.txt;
  
    { time python3 -c "
import findspark
findspark.init()
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc=spark.sparkContext
sc.setLogLevel('WARN')
text_file = sc.textFile('datasets/${filename}')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y).collect()
f = open('output/${filename}_res', 'w')
f.write('\n'.join(map(lambda x: str(x), counts)))
f.close()
sc.stop()
spark.stop()
"; } 2>> time_results.txt
done


