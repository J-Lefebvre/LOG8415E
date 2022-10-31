// package com.maven.eclipse;

import java.io.IOException;
import java.util.*;
import java.util.Map.Entry;
import java.util.HashSet;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class Reduce extends Reducer<IntWritable, RecommendedFriend, IntWritable, Text> {

    /**
    * @param key        the key corresponding to person we want to recommend other friends
    * @param recFriends all the potential recommended friends that were generated through the map
    * @param context    context object, used to output the final recommendation
    * Reduce function, that filters out potential recommendations that are already friends and sorts the rest by number
    * of mutual friends to get the top 10 recommended friends.
    */

    @Override
    public void reduce(IntWritable key, Iterable<RecommendedFriend> recFriends, Context context)
            throws IOException, InterruptedException {

        // Key is the recommended friend, and value is mutual friends count
        HashMap<Integer, Integer> mutualFriendMap = new HashMap<Integer, Integer>();
        HashSet<Integer> friends = new HashSet<Integer>();

        // For each recommendedFriend, populate mutualFriendMap and friends
        for (RecommendedFriend value : recFriends) {
            Integer user = value.recommended;
            Boolean isFriend = value.mutual == -1;

            if(isFriend){
                friends.add(user);
            }

            mutualFriendMap.merge(user, 1, Integer::sum);
        }

        // sortedMutualFriends is populated from mutualFriendMap in descending order of mutual friends count
        // and by key (recommended friend ID) if the values (mutual friends count) are equal.
        SortedMap<Integer, Integer> sortedMutualFriends = new TreeMap<Integer, Integer>(new Comparator<Integer>() {
            @Override
            public int compare(Integer key1, Integer key2) {
                Integer i1 = mutualFriendMap.get(key1);
                Integer i2 = mutualFriendMap.get(key2);
                return ((i1 > i2) || (i1.equals(i2) && key1 < key2)) ? -1 : 1;
            }
        });

        // Populate sortedMap
        for (Entry<Integer, Integer> entry : mutualFriendMap.entrySet()) {
            if(!friends.contains(entry.getKey()))
                sortedMutualFriends.put(entry.getKey(), entry.getValue());
        }

        int index = 0;
        String output_line = "";
        final int RECOMMENDED_FRIENDS_LIMIT = 10;
        
        // Loop through sorted map to build best recommended friends list
        for (Entry<Integer, Integer> entry : sortedMutualFriends.entrySet()) {
        	
        	// Stop looping if limit of recommended friends is reached
        	if (index == RECOMMENDED_FRIENDS_LIMIT)
        		break;
        	
        	// Create output line
        	output_line += (index != 0 ? "," : "") + entry.getKey().toString();
        
        	index++;
        }
        
        // Write output
        context.write(key, new Text(output_line));
    }
}