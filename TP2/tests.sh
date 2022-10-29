# Save wordcount execution time of Ulysses dataset using Hadoop
echo -n "Hadoop - Ulysses" >> time_results.txt;
{ time hadoop jar files/wc.jar WordCount ./input/ ./output 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;

# Save wordcount execution time of Ulysses dataset using Linux
echo -n "Linux - Ulysses" >> time_results.txt;
{ time cat files/pg4300.txt | tr ' ' '\n' | sort | uniq -c 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;

# Loop dataset folder and save wordcount execution time for each dataset using spark
echo '######## SPARK ########' >> time_results.txt;
for file in $(ls ~/files/datasets/)
do
    # remove file extension
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
spark.stop()
"2>1; } 2>> time_results.txt;
echo "" >> time_results.txt;
done;

echo "" >> time_results.txt;
echo "" >> time_results.txt;

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
