// package com.maven.eclipse;

import java.io.IOException;
import java.util.*;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class Map extends Mapper<LongWritable, Text, IntWritable, RecommendedFriend> {

    /**
    * @param key the key, should be empty
    * @param row the row to process
    * @param context objects that allows to write the mapped elements
    * Function that create pairs of potentially recommendable friends.
    * Iterate through all the friend lists, and recommends each user's friend to the other people in it's friend list.
    */

    @Override
    public void map(LongWritable key, Text row, Context context) throws IOException, InterruptedException {

    	// Extract user and list of friend IDs
        String line[] = row.toString().split("\t");
        Integer user = Integer.parseInt(line[0]);
        List<Integer> friends = new ArrayList<Integer>();

        // Check if user has at least 1 friend
        if (line.length > 1) {

        	// Add each friend in list
        	for (String value: line[1].split(",")) {
        		Integer friend = Integer.parseInt(value);
                friends.add(friend);

                // Create pair with mutual friend value of -1 because they are already friends with user
                context.write(new IntWritable(user), new RecommendedFriend(friend, -1));
            }

        	// Create pairs of mutual friends ----> (user, (recommendedFriend, mutualFriend))
            for (int i = 0; i < friends.size(); i++) {
                for (int j = i + 1; j < friends.size(); j++) {
                    context.write(new IntWritable(friends.get(i)), new RecommendedFriend(friends.get(j), user));
                    context.write(new IntWritable(friends.get(j)), new RecommendedFriend(friends.get(i), user));
                }
            }
        }
    }
}