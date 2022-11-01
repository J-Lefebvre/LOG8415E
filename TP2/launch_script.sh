#!/bin/bash

# launch_script.sh automates the installation and setup of Hadoop and Spark on a Linux machine.

# 1. Download and install Java
cd ~;
apt install -y default-jdk;

# 2. Export the JAVA_HOME environment variable
echo "export JAVA_HOME=/usr/lib/jvm/default-java"  >>  ~/.profile;

# 3. Download and install Hadoop
wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz;
tar -xf hadoop-3.3.4.tar.gz -C /usr/local/;

# 4. Export environment variables for Hadoop
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> ~/.profile;
echo "export PATH=\$HADOOP_HOME/bin:\$PATH"  >>  ~/.profile;

source ~/.profile;

echo "export JAVA_HOME=/usr/lib/jvm/default-java" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh;
echo "export HADOOP_HOME=/usr/local/hadoop-3.3.4" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh;

head -n -3 $HADOOP_HOME/etc/hadoop/core-site.xml > tmp.txt && mv tmp.txt $HADOOP_HOME/etc/hadoop/core-site.xml;
head -n -4 $HADOOP_HOME/etc/hadoop/hdfs-site.xml > tmp.txt && mv tmp.txt $HADOOP_HOME/etc/hadoop/hdfs-site.xml;


echo "<configuration><property><name>hadoop.tmp.dir</name><value>/var/lib/hadoop</value></property></configuration>" >> $HADOOP_HOME/etc/hadoop/core-site.xml;
echo "<configuration><property><name>dfs.replication</name><value>1</value></property></configuration>" >> $HADOOP_HOME/etc/hadoop/hdfs-site.xml;

# 5. SSH setup
apt install -y ssh;

service ssh restart;

ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa;
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys;
chmod 0600 ~/.ssh/authorized_keys;

mkdir /var/lib/hadoop;
chmod 777 /var/lib/hadoop;

# 6. HDFS configuration
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
hdfs dfs -mkdir -p sn_input;

# 7. Install git and clone the utilitary repository
apt install git -y;

git clone https://github.com/miboz/files.git;

# 8. Compile WordCount.java and create a JAR file
hadoop com.sun.tools.javac.Main files/WordCount.java;

cd files;

jar cf wc.jar WordCount*.class;

# 9. Compile the Social Network Java files and create a JAR file
cd social_network;

hadoop com.sun.tools.javac.Main *.java;
jar cf sn.jar *.class;

cd ~;

# 10. Installation of Spark dependencies
apt-get update;
apt install python3-pip -y;
pip install pyspark;
pip install findspark;

# 11. Compute the word frequency of the Ulysses dataset using Hadoop and store the execution time
echo -n "Hadoop - Ulysses" >> time_results.txt;
{ time hadoop jar files/wc.jar WordCount ./input/ ./output 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;

# 12. Compute the word frequency of the Ulysses dataset using Linux and store the execution time
echo -n "Linux - Ulysses" >> time_results.txt;
{ time cat files/pg4300.txt | tr ' ' '\n' | sort | uniq -c 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;

# 13. Compute WordCount using Spark on the datasets contained in ~/files/datasets
#     and store the execution times.
echo '######## SPARK ########' >> time_results.txt;
for file in $(ls ~/files/datasets/)
do
  # Remove file extensions
  filename=$(echo $file| cut  -d'.' -f 1);
  echo -n $filename >> time_results.txt;
  { time python3 -c "
import findspark
import shutil
import os
from pyspark.sql import SparkSession
spark = SparkSession.builder.master('local').appName('FirstProgram').getOrCreate()
sc=spark.sparkContext
text_file = sc.textFile('files/datasets/${file}')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)
if os.path.exists('output/${filename}_spark_res/'):
  shutil.rmtree('output/${filename}_spark_res/')
counts.saveAsTextFile('output/${filename}_spark_res/')
sc.stop()
spark.stop()"
2>1; } 2>> time_results.txt;
  echo "" >> time_results.txt;
done;

echo "" >> time_results.txt;
echo "" >> time_results.txt;

# 14. Compute WordCount using Hadoop on the datasets contained in ~/files/datasets
#     and store the execution times.
echo '######## HADOOP ########' >> time_results.txt;
for file in $(ls ~/files/datasets/)
do
  echo -n $file >> time_results.txt;
  hadoop fs -rm -r ./input/;
  hadoop fs -rm -r ./output_$file/;
  hdfs dfs -mkdir -p input;
  hadoop fs -cp ~/files/datasets/$file ~/input/;
  { time hadoop jar files/wc.jar WordCount ./input/ ./output_$file 2>1; } 2>> time_results.txt;
  echo "" >> time_results.txt;
done;

# 15. Execution of the Social Network problem with Hadoop
hadoop fs -cp ~/files/pg4300.txt ~/input;
hadoop fs -cp ~/files/social_network/soc-LiveJournal1Adj.txt ~/sn_input;

source ~/.profile;


# To run the friend recommendation on ec2
#hadoop jar files/social_network/sn.jar PeopleYouMightKnow ./sn_input/ ./sn_output


## To run the friend recommendation locally
# cd files;
# cd social_network;
# hadoop com.sun.tools.javac.Main *.java;
# jar cf sn.jar *.class;
# cd ..;
# cd ..;
# rm -r sn_output;
# hadoop jar ./files/social_network/sn.jar PeopleYouMightKnow ./sn_input/ ./sn_output