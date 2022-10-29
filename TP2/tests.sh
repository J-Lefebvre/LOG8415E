# Save wordcount execution time of Ulysses dataset using Hadoop
echo -n "Hadoop - Ulysses" >> time_results.txt;
{ time hadoop jar files/wc.jar WordCount ./input/ ./output 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;

# Save wordcount execution time of Ulysses dataset using Linux
echo -n "Linux - Ulysses" >> time_results.txt;
{ time cat files/pg4300.txt | tr ' ' '\n' | sort | uniq -c 2>1; } 2>> time_results.txt;

echo "" >> time_results.txt;
