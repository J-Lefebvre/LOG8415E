// package com.maven.eclipse;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;


public class PeopleYouMightKnow {

    /**
    * @param args Arguments of java executable, the first one is the input path, and the second one the output path
    * Main function executed when running the program
    */
    public static void main(String[] args) throws Exception {
        Configuration newConfiguration = new Configuration();

        Job newJob = Job.getInstance(newConfiguration, "PeopleYouMightKnow");

        // link the main logic classes that will be used
        newJob.setJarByClass(PeopleYouMightKnow.class);
        newJob.setMapperClass(Map.class);
        newJob.setReducerClass(Reduce.class);

        // link the helper classes that will be used
        newJob.setInputFormatClass(TextInputFormat.class);
        newJob.setOutputFormatClass(TextOutputFormat.class);
        newJob.setOutputKeyClass(IntWritable.class);
        newJob.setOutputValueClass(RecommendedFriend.class);

        FileSystem newOutFileSystem = new Path(args[1]).getFileSystem(newConfiguration);
        newOutFileSystem.delete(new Path(args[1]), true);

        FileInputFormat.addInputPath(newJob, new Path(args[0]));
        FileOutputFormat.setOutputPath(newJob, new Path(args[1]));

        newJob.waitForCompletion(true);
    }
}
