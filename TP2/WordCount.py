import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.master('local').appName('Firstprogram').getOrCreate()
sc=spark.sparkContext

text_file = sc.textFile('files/pg4300.txt')
counts = text_file.flatMap(lambda line: line.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y).collect()

f = open('output/spark_part-r-00000', 'w')
f.write('\n'.join(map(lambda x: str(x), counts)))
f.close()

sc.stop()
spark.stop()