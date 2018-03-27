import java.io.*;

public class CompressTest
{
	public static void main(String args[])
	{
		try
		{
			Process p = Runtime.getRuntime().exec("python compress.py");
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));

			String s = null;
		
			while ((s=input.readLine()) != null)
			{
				System.out.println(s);
			}
		} catch(IOException e)
		{
			System.out.println("IO exception");
			e.printStackTrace();
		}
	}
}
