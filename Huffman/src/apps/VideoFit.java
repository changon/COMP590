package apps;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Map;

import models.Unsigned8BitModel;
import codec.HuffmanEncoder;
import codec.SymbolDecoder;
import codec.SymbolEncoder;
import models.Symbol;
import models.SymbolModel;
import models.Unsigned8BitModel.Unsigned8BitSymbol;
import io.InsufficientBitsLeftException;
import io.BitSink;
import io.BitSource;
import codec.ArithmeticDecoder;
import codec.ArithmeticEncoder;
import codec.HuffmanDecoder;
import io.InputStreamBitSource;
import io.OutputStreamBitSink;

public class VideoFit {

	public static void main(String[] args) throws IOException, InsufficientBitsLeftException {
		String controlDir = "/Users/Raphael/source/COMP590/code_base/comp590sp18/Huffman/src/";
		controlDir += "controlFile.inp";
		FileInputStream controlIn = new FileInputStream(controlDir);
		String base = "";
		int content;
		while ((content = controlIn.read()) != -1) {
			// convert to char and display it
			base += (char) content;
		}
		base = base.replace("\n", "");
		//System.out.println('"'+base+'"');
		
		//String fileName="/Users/kmp/tmp/" + base + ".450p.yuv";
		//String fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".450p.yuv";
		String fileName="/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/" + base + ".residuals";
		File file = new File(fileName);
		int width = 800;
		int height = 450;
		int num_frames = 150;

		Unsigned8BitModel model = new Unsigned8BitModel();

		InputStream training_values = new FileInputStream(file);
		int[][] current_frame = new int[width][height];

		// build prob. model from our curve fit residuals
		for (int f=0; f < num_frames; f++) {
			System.out.println("Training frame " + f);
			current_frame = readFrame(training_values, width, height);
			trainModelWithFrame(model, current_frame); //increment probability model information
		}
		training_values.close();		

		//HuffmanEncoder encoder = new HuffmanEncoder(model, model.getCountTotal());
		//Map<Symbol, String> code_map = encoder.getCodeMap();

		SymbolEncoder encoder = new ArithmeticEncoder(model);

		Symbol[] symbols = new Unsigned8BitSymbol[256];
		for (int v=0; v<256; v++) {
			SymbolModel s = model.getByIndex(v);
			Symbol sym = s.getSymbol();
			symbols[v] = sym;

			long prob = s.getProbability(model.getCountTotal());
			System.out.println("Symbol: " + sym + " probability: " + prob + "/" + model.getCountTotal());
		}			

		InputStream message = new FileInputStream(file);

		String outputDir = "/Users/Raphael/source/COMP590/data/Raw Video Samples/" + base + "/";
		File out_file = new File(outputDir + base + "-KMPcompressed.dat");
		OutputStream out_stream = new FileOutputStream(out_file);
		BitSink bit_sink = new OutputStreamBitSink(out_stream);

		current_frame = new int[width][height];

		for (int f=0; f < num_frames; f++) {
			System.out.println("Encoding frame difference " + f);
			current_frame = readFrame(message, width, height);
			encodeFrameDifference(current_frame, encoder, bit_sink, symbols);
		}

		message.close();
		encoder.close(bit_sink);
		out_stream.close();

		BitSource bit_source = new InputStreamBitSource(new FileInputStream(out_file));
		OutputStream decoded_file = new FileOutputStream(new File(outputDir + base + "-KMPdecoded.dat"));

		//SymbolDecoder decoder = new HuffmanDecoder(encoder.getCodeMap());
		SymbolDecoder decoder = new ArithmeticDecoder(model);

		current_frame = new int[width][height];

		for (int f=0; f<num_frames; f++) {
			System.out.println("Decoding frame " + f);
			current_frame = decodeFrame(decoder, bit_source, width, height);
			
			// decoded file has residuals. 
			// get back by = (residual + int(prediction)) mod 256

			outputFrame(current_frame, decoded_file);
		}

		decoded_file.close();
		

	}

	private static int[][] readFrame(InputStream src, int width, int height) 
			throws IOException {
		int[][] frame_data = new int[width][height];
		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				frame_data[x][y] = src.read();
			}
		}
		return frame_data;
	}

	private static int[][] frameDifference(int[][] prior_frame, int[][] current_frame) {
		int width = prior_frame.length;
		int height = prior_frame[0].length;

		int[][] difference_frame = new int[width][height];

		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				difference_frame[x][y] = ((current_frame[x][y] - prior_frame[x][y])+256)%256;
			}
		}
		return difference_frame;
	}

	private static void trainModelWithFrame(Unsigned8BitModel model, int[][] frame) {
		int width = frame.length;
		int height = frame[0].length;
		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				model.train(frame[x][y]);
			}
		}
	}

	private static void encodeFrameDifference(int[][] frame, SymbolEncoder encoder, BitSink bit_sink, Symbol[] symbols) 
			throws IOException {

		int width = frame.length;
		int height = frame[0].length;

		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				encoder.encode(symbols[frame[x][y]], bit_sink);
			}
		}
	}

	private static int[][] decodeFrame(SymbolDecoder decoder, BitSource bit_source, int width, int height) 
			throws InsufficientBitsLeftException, IOException {
		int[][] frame = new int[width][height];
		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				frame[x][y] = ((Unsigned8BitSymbol) decoder.decode(bit_source)).getValue();
				//int prediction = (int) lin_combo

				//int prediction = 0;
				//frame[x][y] = (frame[x][y] + prediction) % 256;
// get back by x = (residual + int(prediction)) mod 256
			}
		}
		return frame;
	}

	private static int[][] reconstructFrame(int[][] prior_frame, int[][] frame_difference) {
		int width = prior_frame.length;
		int height = prior_frame[0].length;

		int[][] frame = new int[width][height];
		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				frame[x][y] = (prior_frame[x][y] + frame_difference[x][y])%256;
			}
		}
		return frame;
	}

	private static void outputFrame(int[][] frame, OutputStream out) 
			throws IOException {
		int width = frame.length;
		int height = frame[0].length;
		for (int y=0; y<height; y++) {
			for (int x=0; x<width; x++) {
				out.write(frame[x][y]);
			}
		}
	}
}
