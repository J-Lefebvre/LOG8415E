// package com.maven.eclipse;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class RecommendedFriend implements Writable {
	public Integer recommended;
	public Integer mutual;

    /**
    * RecommendedFriend Constructor
    * @param Integer recommended the recommended friend
    * @param Integer mutual the mutual friend
    * Builds a RecommendedFriend object with the specified parameters
    */
	public RecommendedFriend(Integer recommended, Integer mutual) {
		this.recommended = recommended;
		this.mutual = mutual;
	}

    /**
    * RecommendedFriend Constructor
    * Builds a RecommendedFriend object with the default parameters (-1, -1)
    */
	public RecommendedFriend() {
		this.recommended = new Integer(-1);
		this.mutual = new Integer(-1);
	}

    /**
    * @param input  the output to be written to
    * Writes two saved value to an output
    */
	@Override
	public void write(DataOutput output) throws IOException {
		output.writeInt(recommended);
		output.writeInt(mutual);
	}

    /**
    * @param input  the input to be red
    * Reads the two fields of an input and stores them
    */
	@Override
	public void readFields(DataInput input) throws IOException {
		recommended = input.readInt();
		mutual = input.readInt();
	}
}