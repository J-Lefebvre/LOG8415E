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
