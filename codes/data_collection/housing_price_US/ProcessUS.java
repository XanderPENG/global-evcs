package github;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.serializer.SerializerFeature;

import java.io.BufferedReader;

//import net.sf.json.JSONArray;

import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.Reader;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Random;
import java.util.Stack;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import org.springframework.core.io.ClassPathResource;
import org.springframework.util.StringUtils;
public class ProcessUS {
	
	/**
	 * 1.读入文件，按行处理
	 * 2.判定Id是否已存在，若已存在则舍弃
	 * 3.判定数据是否完整，若不完整直接舍弃（1.经纬度不完整；2.计算价格）
	 * 4.若完整则计算价格
	 * 5.将Id添加到列表，把数据写入文档
	 * @throws IOException 
	 * 
	 */
	public static void main(String[] args) throws IOException {
		//读入已有id
		ArrayList<String> stationExist = new ArrayList<String>();
		File InputFileId = new File("USRealEstate0526.csv");
		DataInputStream inId = new DataInputStream(new FileInputStream(InputFileId));
		BufferedReader brId = new BufferedReader(new InputStreamReader(inId, "UTF-8"));
		
		int isFirstId = 1;
		String sId = null;
		while ((sId = brId.readLine()) != null) {
			if (isFirstId == 1) {
				isFirstId = 0;
				// 跳过文件头
				continue;
			}
			String[] sList = sId.split(",");
			stationExist.add(sList[0]);
		}
		brId.close();
		inId.close();
		
		//输出文件
		File OutputFile = new File("USRealEstate0526.csv");
		FileOutputStream out = null;
		OutputStreamWriter osw = null;
		BufferedWriter bw = null;
		out = new FileOutputStream(OutputFile, true);
		osw = new OutputStreamWriter(out, "UTF-8");
		bw = new BufferedWriter(osw);
		
		
		// 读入文件
		File InputFile = new File("USRealEstateAll1.csv");
		DataInputStream in = new DataInputStream(new FileInputStream(InputFile));
		BufferedReader br = new BufferedReader(new InputStreamReader(in, "UTF-8"));
		
		int isFirst = 1;
		String s = null;
		while ((s = br.readLine()) != null) {
			if (isFirst == 1) {
				isFirst = 0;

				// 跳过文件头
				continue;
			}
			//跳过已有数据
			String[] sList = s.split(",");
			if(stationExist.contains(sList[0])) {
				System.out.println("skip data already exist!!!");
				continue;
			}
			//跳过存在空值的数据
			if(sList[6].equals("null")||sList[7].equals("null")||sList[23].equals("null")||sList[24].equals("null")||sList[25].equals("null")||sList[29].equals("null")||sList[6]==null||sList[6].equals("")) {
				
				//System.out.println("skip data with null");
				continue;
			}
			
			//计算房价（单位面的价格）
			float pricePer=0;
			float price = Float.parseFloat(sList[25]);
			float area = Float.parseFloat(sList[29]);
			if(area == 0) {
				continue;
			}else {
				pricePer = price/area;
			}
			
			//
			stationExist.add(sList[0]);
			bw.write(pricePer+","+s+"\r");
			//System.out.println("new data:"+sList[0]);
		}
		bw.close();
		
		

		
	}

}
