package github;

//import net.sf.json.JSONObject;
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
import java.io.FileOutputStream;
import org.springframework.core.io.ClassPathResource;
import org.springframework.util.StringUtils;

class USRealEstate {
	public static String jsonFilePath = "";


	public static ArrayList<String> readUSJsonFileToArray(String outputFile) {
		ArrayList<String> staionList = new ArrayList();

		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < outputFile.length(); i++) {

			sb.append(outputFile.substring(i, i + 1));
			String writeLine = "";
			if (sb.toString().contains("\"mapResults\":[")||sb.toString().contains("\"listResults\":[")
					||sb.toString().contains("\"relaxedResults\":[")) {
				sb.delete(0, sb.length());// start from first result
			}
			
			if (sb.toString().contains(",{\"zpid\"")
					|| (sb.toString().contains("}],") && sb.toString().contains("zpid"))
					|| sb.toString().contains(",{\"buildingId\"")) {

				int minorToJson = 0;
				if (sb.toString().contains("\"carouselPhotos\":[")&&sb.toString().contains("}],")) {
					System.out.println(sb.toString());
					int head = sb.toString().indexOf("\"carouselPhotos");
					if(head>-1) {
						sb.delete(head, sb.length() );		
						continue;
					}
					
				}
				if (sb.toString().contains(",{\"zpid\"")) {
					if (sb.toString().contains("{\"buildingId\"")) {
						sb.delete(0, sb.length() - 7);
						continue;
					}
					minorToJson = 8;
				} else if (sb.toString().contains("}],")) {
					if (sb.toString().contains("{\"buildingId\"")) {
						sb.delete(0, sb.length() - 1);
						continue;
					}
					minorToJson = 2;
				} else if (sb.toString().contains("{\"buildingId\"")) {
					minorToJson = 14;
				} 
				
				
				String param = sb.toString();

				int indexofId=param.toString().indexOf("{\"zpid\"");
				if(indexofId>0) {
					param = param.substring(indexofId,param.length());
				}
				
				param = param.substring(0, param.length() - minorToJson);
				if(param.toString().contains(",{\"price\"")) {
					int endIndex=param.toString().indexOf(",{\"price\"");
					param=param.substring(0,endIndex);
				}
				System.out.println(param);
				JSONObject parse = (JSONObject) JSONObject.parse(param);
				JSONObject variableData = new JSONObject();
				if (String.valueOf(parse.get("variableData")).isEmpty()
						|| String.valueOf(parse.get("variableData")) == "null") {
					variableData.put("type", "null");
					variableData.put("text", "null");

				} else {
					variableData = parse.getJSONObject("variableData");
				}
				JSONObject hdpData = parse.getJSONObject("hdpData");		
				JSONObject homeInfo = new JSONObject();
				JSONObject listing_sub_type = new JSONObject();
				boolean isHomeInfoEmpty=false;
				String datePriceChanged="";
				if(String.valueOf(parse.get("hdpData")).isEmpty()
						|| String.valueOf(parse.get("hdpData")) == "null") {
					isHomeInfoEmpty=true;
				}else {
					homeInfo = hdpData.getJSONObject("homeInfo");
					listing_sub_type = homeInfo.getJSONObject("listing_sub_type");
					if(!String.valueOf(homeInfo.get("datePriceChanged")).isEmpty()
							&& String.valueOf(homeInfo.get("datePriceChanged")) != "null") {
						datePriceChanged=homeInfo.get("datePriceChanged").toString();
					}
				}
				JSONObject latLong = parse.getJSONObject("latLong");
				
				 
				if(isHomeInfoEmpty) {
					writeLine += parse.get("zpid") + "," + String.valueOf(parse.get("price")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
				+ String.valueOf(parse.get("priceLabel")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ parse.get("beds")  + ","
				+String.valueOf(parse.get("baths")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
				+ String.valueOf(parse.get("area")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ latLong.get("latitude") + "," + latLong.get("longitude") + "," + parse.get("statusType") + ","
							+ String.valueOf(parse.get("statusText")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," + parse.get("isFavorite") + ","
							+ parse.get("isUserClaimingOwner") + "," + parse.get("isUserConfirmedClaim") + ","
							+ String.valueOf(parse.get("imgSrc")).replace(",", "").replace("\r", " ").replace("\n"," ") + " " + "," + parse.get("hasImage") + "," + parse.get("visited") + ","
							+ parse.get("listingType") + "," + String.valueOf(variableData.get("type")) + ","
							+ String.valueOf(variableData.get("text")).replace(",", " ").replace("\r", " ").replace("\n",
									" ")
							+ "," + "null" + "," + "null" + "," + "null" + ","
							+ "null" + "," + "null" + "," + "null" + ","
							+ "null" + "," + "null" + "," + "null" + ","
							+ "null" + "," + "null" + "," + "null"+ ","+"null"
							+ "," + "null" + "," +"null" + ","+"null"+ ","+"null"+ ","
							+ "null" + "," + "null" + ","

							+ "null" + "," + "null" + ","
							+ "null"+ "," + "null" + ","
							+ "null" + "," + "null" + ","
							+ "null" + "," + "null" + "," +"null"
							+ "," + "null" + "," + "null" + ","
							+ "null" + ","

							+ parse.get("detailUrl") + "," + parse.get("pgapt") + "," + parse.get("sgapt") + ","
							+ parse.get("has3DModel") + "," + parse.get("hasVideo") + "," + parse.get("isHomeRec") + ","
							+ parse.get("address") + "," + parse.get("hasAdditionalAttributions") + ","
							+ parse.get("isFeaturedListing") + "," + parse.get("availabilityDate");
				}else {
					writeLine += parse.get("zpid") + "," + String.valueOf(parse.get("price")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
				+ String.valueOf(parse.get("priceLabel")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ parse.get("beds") + "," +  String.valueOf(parse.get("baths")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
				+ String.valueOf(parse.get("area")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ latLong.get("latitude") + "," + latLong.get("longitude") + "," + parse.get("statusType") + ","
							+ String.valueOf(parse.get("statusText")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," + parse.get("isFavorite") + ","
							+ parse.get("isUserClaimingOwner") + "," + parse.get("isUserConfirmedClaim") + ","
							+ String.valueOf(parse.get("imgSrc")).replace(",", "").replace("\r", " ").replace("\n"," ") + " " + "," + parse.get("hasImage") + "," + parse.get("visited") + ","
							+ parse.get("listingType") + "," + String.valueOf(variableData.get("type")) + ","
							+ String.valueOf(variableData.get("text")).replace(",", " ").replace("\r", " ").replace("\n",
									" ")
							+ "," + homeInfo.get("zpid") + "," + homeInfo.get("zipcode") + "," + homeInfo.get("city") + ","
							+ homeInfo.get("state") + "," + homeInfo.get("latitude") + "," + homeInfo.get("longitude") + ","
							+ String.valueOf(homeInfo.get("price")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ datePriceChanged + ","
							+ String.valueOf(homeInfo.get("bathrooms")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ String.valueOf(homeInfo.get("bedrooms")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ String.valueOf(homeInfo.get("livingArea")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ String.valueOf(homeInfo.get("homeType")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ homeInfo.get("homeStatus")
							+ "," + homeInfo.get("daysOnZillow") + "," + homeInfo.get("isFeatured") + ","
							+ homeInfo.get("shouldHighlight") + "," + listing_sub_type.get("is_bankOwned") + ","
							+ String.valueOf(homeInfo.get("priceReduction")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ homeInfo.get("isUnmappable") + "," + homeInfo.get("isPreforeclosureAuction") + ","
							+ String.valueOf(homeInfo.get("homeStatusForHDP")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ String.valueOf(homeInfo.get("priceForHDP")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ String.valueOf(homeInfo.get("priceChange")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ homeInfo.get("isNonOwnerOccupied") + "," + homeInfo.get("isPremierBuilder") + ","
							+ homeInfo.get("isZillowOwned") + "," 
							+ String.valueOf(homeInfo.get("currency")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ homeInfo.get("country")+ "," 
							+ String.valueOf(homeInfo.get("taxAssessedValue")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ String.valueOf(homeInfo.get("lotAreaValue")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","
							+ String.valueOf(homeInfo.get("lotAreaUnit")).replace(",", "").replace("\r", " ").replace("\n"," ") + ","

							+ String.valueOf(parse.get("detailUrl")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ parse.get("pgapt") + "," + parse.get("sgapt") + ","
							+ parse.get("has3DModel") + "," + parse.get("hasVideo") + "," + parse.get("isHomeRec") + ","
							+ String.valueOf(parse.get("address")).replace(",", "").replace("\r", " ").replace("\n"," ") + "," 
							+ parse.get("hasAdditionalAttributions") + ","
							+ parse.get("isFeaturedListing") + "," + parse.get("availabilityDate");
				}
			
				staionList.add(writeLine);


				sb.delete(0, sb.length() - minorToJson + 1);
			}
		}

		return staionList;

	}

	

	public static void main(String[] args) throws IOException, InterruptedException {

		/**
		 * 经纬度转换 test
		 */

		/**
		 * 读取原有数据
		 */
		File OutputFile = new File("USRealEstateAll1.csv");
		// Writter
		FileOutputStream out = null;
		OutputStreamWriter osw = null;
		BufferedWriter bw = null;
		FileReader fileReader = new FileReader(OutputFile);
		DataInputStream in = new DataInputStream(new FileInputStream(OutputFile));
		BufferedReader br = new BufferedReader(new InputStreamReader(in, "UTF-8"));
		// 定义文件名格式并创建
		out = new FileOutputStream(OutputFile, true);
		osw = new OutputStreamWriter(out, "UTF-8");
		bw = new BufferedWriter(osw);

		ArrayList<String> stationExist = new ArrayList<String>();
		int isFirst = 1;
		String s = null;
		while ((s = br.readLine()) != null) {
			if (isFirst == 1) {
				isFirst = 0;

				// 跳过文件头
				continue;
			}
			String[] sList = s.split(",");
			stationExist.add(sList[0]);
		}

		/**
		 * 数据爬取
		 */

		Random r = new Random();

		/**
		 * State
		 * 
		 * Alaska Alabama Arkansas American Samoa Arizona California Colorado
		 * Connecticut Delaware Florida Georgia Guam Hawaii Iowa Idaho Illinois Indiana
		 * Kansas Kentucky Louisiana Massachusetts Maryland Maine Michigan Minnesota
		 * Missouri Northern Mariana Islands Mississippi Montana North Carolina North
		 * Dakota Nebraska New Hampshire New Jersey New Mexico Nevada NewYork Ohio
		 * Oklahoma Oregon Pennsylvania Puerto Rico Rhode Island SouthCarolina SouthDakota 
		 * Tennessee Texas Utah Virginia Virgin Islands Vermont Washington
		 * Washington,DC Wisconsin West Virginia Wyoming
		 * 
		 **/
	//Los Angeles: -118.60 ~ -117.60; 33.7 ~ 34.3
		/**
		 * test 按州进行爬取
		 */

		int requestId=0;
		int numberThisTime=0;
		String stopAt = "";
		/*
		 * 修改这里的行和列
		 */
		for(int round=1;round<11;round++) {
			int numberThisRound=0;
			
			for(int roundy=0;roundy<40;roundy++) {
				 
				//用于从某一行指定的列开始
//				if(round==49&&roundy==0) {
//					roundy=116;
//				}
				//跳过部分空白区域


				/**
				 * Jiaxing 2023/03/07
				 * 
				 * 爬取美国数据
				 * 1.第一次
				 * 从west：-117.05000000001 到-117.05000000001 + 21.8 = -95.25
				 * 从south：32.55310590000001 到 32.55310590000001 + 16.5 = 49.0531
				 * 
				 * 2.第二次
				 * 从west：-117.05000000001 开始，每次循环减0.1 到 - 124.80， 共78次
				 * 从south：49.0531 开始，每次循环减0.1，到32.55，共165次
				 * 
				 * 3.第三次 - 重跑第一次部分区域
				 * 从west：-112.89000000001 到 -117.05000000001 + 21.8 = -95.25 共177次
				 * 从south：32.55310590000001  到 32.55310590000001 + 16.5 = 49.0531 共165次
				 * 
				 * 4.第四次
				 * 从west：-95.25000000001 到 -95.25000000001 + 14.5 = -80.75 共145次
				 * 从south：28.97000000000001  到 28.97000000000001 + 20.1 = 49.0531 共201次
				 * 
				 * 5.第五次 爬取最右侧未爬区域
				 * 从west：-80.75000000001 到 -80.75000000001 + 13.9 = -66.85 共139次
				 * 从south：32.12000000000001  到 32.12000000000001 + 15.3 = 47.42 共153次
				 * 
				 * 6.第六次，下面剩余部分
				 * 分为两块，
				 * 一块经度范围位：-95.25000000001 到 -112.89000000001，纬度在32.55310590000001以下
				 * 
				 * 爬取 经度-95.25到 -112.89，纬度从32.55 到 31.28 部分 x 共 177次，y 共 13次
				 *  从 -105.90 开始，爬取纬度从32.55 到 25.78 部分 ； 从 x 大于 69开始 ,y 共 68次
				 *  从 -97.14 （-97.14，25.78）开始，（-94.99，29.16） - - 1.57 （经度每增加1，纬度的下限增加1.57, y= 1.57* x + 178.2898）从157开始
				 * 
				 * 第二块，纬度在28.97000000000001以下 到25.08046，经度范围为-80.75 到 -82.85
				 *  从 -82.85 开始， 到 -80.75， 共 21次
				 *  从 25.08046 开始 到 28.97， 共 39次
				 *  其中，当 x为0时，跳过24次，x为16时，开始不跳过，故当x小于16时，跳过 y = -1.5*x + 24 次 
				 * 
				 * 补爬1： 
				 * 经度-71.7 到 -70.6部分 共 11次
				 * 从south：41.10000000000001  到 45.10000000000001  共40次
				 * 
				 */
		
				double west = -71.70 + round * 0.1;// 
				double east = west+0.101;
				
				double south = 41.12000000000001 + roundy * 0.1;//
				double north = south+0.101;

				requestId+=1;
				if(requestId>300) {
					requestId=1;
				}
				//Url-1
				String dataUrl="https://www.zillow.com/search/GetSearchPageState.htm?searchQueryState=%7B%22"
						+ "usersSearchTerm%22%3A%22New%20York%2C%20NY%22%2C%22mapBounds%22%3A%7B%22west%22%3A"
						+ west//-117.54509639395776
						+"%2C%22east%22%3A"
						+ east//-117.19456386221948
						+"%2C%22south%22%3A"
						+ south//33.879242433771616
						+"%2C%22north%22%3A"
						+ north//34.233935172914336
						+ "%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sortSelection%22%3A%7B%22value%22%3A%22"
						+ "days%22%7D%2C%22isAllHomes%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22"
						+ "mapZoom%22%3A15%7D&wants={%22cat1%22:[%22listResults%22,%22mapResults%22],%22cat2%22:[%22total%22],%22regionResults%22:[%22regionResults%22]}&requestId="
						+ requestId;

				System.out.println("round:"+round+",roundy:"+roundy+",west:"+west+",south:"+south);
				String resultUS = sendGetUSRealEstate(dataUrl);
				if (resultUS.contains("zpid")) {// 说明有数据
					if(!stopAt.equals("")) {
						stopAt="";
					}
					System.out.println("新读取..");
					ArrayList<String> listFromUS = readUSJsonFileToArray(resultUS);
					int numberThisRoundy=0;
					for (int i = 0; i < listFromUS.size(); i++) {
						if (isFirst == 1) {
							isFirst = 0;
							// 跳过文件头
							continue;
						}
						// System.out.println(s);
						String[] sList = listFromUS.get(i).split(",");
						// System.out.println(sList[4]+","+sList[0]);
						if (!stationExist.contains(sList[0])) {
							stationExist.add(sList[0]);
							bw.write(listFromUS.get(i) + "\r\n");
							numberThisRoundy+=1;
							numberThisTime+=1;
							numberThisRound+=1;
						} else {
						}
						bw.flush();
						
					}
					System.out.println("这一roundy共添加"+numberThisRoundy+"条新数据，这一round共添加："+numberThisRound+"条数据，总共添加了："+numberThisTime+"条数据");
					stopAt=" StopAt:Round:"+round+",Roundy:"+roundy;
				}
				else {
					
					System.out.println("round:"+round+",roundy:"+roundy+",无数据. "+"这一round共添加："+numberThisRound+"条数据，总共添加了："+numberThisTime+"条数据"+stopAt);
				}

				Thread.sleep(3000);
				if(round%10==0) {
					Thread.sleep(10000);
				}
			}
			System.out.println("End of round"+round);
			Thread.sleep(20000);
		}
		System.out.println("这次运行程序共添加"+numberThisTime+"条新数据");

		bw.close();
		osw.close();
		out.close();
		/**
		 * 数据合并
		 */


	}

	public static String sendGetUSRealEstate(String url) {
		String result = "";
		BufferedReader in = null;
		System.out.println("Start request data:"+url);
		try {
			String urlNameString = url;
			URL realUrl = new URL(urlNameString);
			URLConnection connection = realUrl.openConnection();

			connection.addRequestProperty("Cookie",
					"x-amz-continuous-deployment-state=AYABeII4vijqDZRjUotH9Pqon6EAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzAxNTk1MzcxVEJNNTJaWDdPU09PAAEAAkNEABpDb29raWUAAACAAAAADPe/DPm74Clm5iWURwAw4xey/aBOoprLTZ0EIYPydFzJZQ2d5KtMKEgK5hAEY00ptVFk/MLRPotRfutT2ulmAgAAAAAMAAQAAAAAAAAAAAAAAAAAAFS07UeWA+WZFZ/v2ndN8rr/////AAAAAQAAAAAAAAAAAAAAAQAAAAxIVDxyz6HBk10940TAVIr00dcpZ8bpH3MUVWHG; AWSALB=U1L5Yegn0va0eiP2VvrBQYvwemdz50lUPqDyrdddSFORT2Hoa1t+wFGkTET4W7qZ2H20Velov5VevNklMO0xwTvIm81wOr+57W/aTywMNDfYrpWAmSewQCfOTUv/; AWSALBCORS=U1L5Yegn0va0eiP2VvrBQYvwemdz50lUPqDyrdddSFORT2Hoa1t+wFGkTET4W7qZ2H20Velov5VevNklMO0xwTvIm81wOr+57W/aTywMNDfYrpWAmSewQCfOTUv/; JSESSIONID=67F9687385C0701B39DEF834862F568C; search=6|1684805975021|rect=32.22100000000001%2C-80.64900000001%2C32.12000000000001%2C-80.75000000001&disp=map&mdm=auto&p=1&sort=days&z=1&listPriceActive=1&fs=1&fr=0&mmm=0&rs=0&ah=0&singlestory=0&housing-connector=0&abo=0&garage=0&pool=0&ac=0&waterfront=0&finished=0&unfinished=0&cityview=0&mountainview=0&parkview=0&waterview=0&hoadata=1&zillow-owned=0&3dhome=0&featuredMultiFamilyBuilding=0&commuteMode=driving&commuteTimeOfDay=now								; zguid=24|$2988b544-5fae-43bd-8a79-dd9210ec3c38; zgsession=1|d3953133-10fe-44c0-ba11-257c17dadd49; x-amz-continuous-deployment-state=AYABeKlL0F5+AvWgkzkMCaVqZjEAPgACAAFEAB1kM2Jsa2Q0azB3azlvai5jbG91ZGZyb250Lm5ldAABRwAVRzAxNTk1MzcxVEJNNTJaWDdPU09PAAEAAkNEABpDb29raWUAAACAAAAADJhAGAuaq1fKNrAT0QAwZ1Tr6+A69MmRTvMmmMedv3+RMKBlbN5SYgf5yPg27PVPa/x9I1Znthc75stTuAx6AgAAAAAMAAQAAAAAAAAAAAAAAAAAADipbnT4fM7WlhVyVk4yE8n/////AAAAAQAAAAAAAAAAAAAAAQAAAAzuVzF6xNONxdQs4bm1di85p4sK5IAL8ouXuWM1");
			//Cookie

			connection.setRequestProperty("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6");
			connection.setRequestProperty("user-agent",
					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56");
			connection.connect();			
			in = new BufferedReader(new InputStreamReader(connection.getInputStream(), "UTF-8"));
			String line;
			while ((line = in.readLine()) != null) {
				result += line;
			}
			if (result.contains("mapResults")) {
				System.out.println("爬取到结果");
				if(!result.contains("zpid")) {
					System.out.println("结果中不含数据");
				}
				return result;
			}else {
				System.out.println(result);
				System.out.println("结果不含MapResults");
			}

		} catch (Exception e) {
			System.out.println("发送GET请求出现异常！" + e);
			e.printStackTrace();
		}
		finally {
			try {
				if (in != null) {
					in.close();
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}
		return result;
	}

	public static String lonAndLatToWGS84Web(double lon, double lat) {

		double x = lon * 20037508.34 / 180;
		double y = Math.log(Math.tan((90 + lat) * Math.PI / 360)) / (Math.PI / 180);
		y = y * 20037508.34 / 180;
		return (x + "," + y);

	}

	public static String WGS84WebToLonAndLat(double x, double y) {
		double lon = x / 20037508.34 * 180;
		double lat = y / 20037508.34 * 180;
		lat = 180 / Math.PI * (2 * Math.atan(Math.exp(lat * Math.PI / 180)) - Math.PI / 2);
		return (lon + "," + lat);

	}

	public boolean isValid(String s) {// 用以匹配一组数据
		Stack<Character> st = new Stack<>();
		for (char c : s.toCharArray()) {
			if (c == '(')
				st.push(')');
			else if (c == '[')
				st.push(']');
			else if (c == '{')
				st.push('}');
			else if (st.isEmpty() || c != st.pop())
				return false;
		}
		return st.isEmpty();
	}

	public static boolean createJsonFile(String jsonData, String filePath) {

		boolean flag = true;
		try {
			File file = new File(filePath);
			if (file.exists()) { 
				file.delete();
			}
			boolean t = file.createNewFile();
			Writer write = new OutputStreamWriter(new FileOutputStream(file), "UTF-8");
			write.write(jsonData);
			write.flush();
			write.close();
		} catch (Exception e) {
			flag = false;
			e.printStackTrace();
		}
		return flag;
	}

	public static String sendGetEC(String url, String param) {
		String result = "";
		BufferedReader in = null;
		try {
			String urlNameString = url + "?" + param;

			URL realUrl = new URL(urlNameString);

			URLConnection connection = realUrl.openConnection();
					
			connection.setRequestProperty("Accept",
					"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9");
			connection.setRequestProperty("Connection", "Keep-Alive");
			connection.setRequestProperty("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6");
			connection.setRequestProperty("user-agent",
					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44");

			connection.connect();

			in = new BufferedReader(new InputStreamReader(connection.getInputStream(), "UTF-8"));
			String line;
			while ((line = in.readLine()) != null) {
				result += line;
			}
			if (result.contains("layerId")) {
				return result;

			}

		} catch (Exception e) {
			System.out.println("发送GET请求出现异常！" + e);
			e.printStackTrace();
		}
		finally {
			try {
				if (in != null) {
					in.close();
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}
		return result;
	}

	public static String sendGet(String url, String param) {
		String result = "";
		BufferedReader in = null;
		try {
			String urlNameString = url + "?" + param;
			URL realUrl = new URL(urlNameString);
			URLConnection connection = realUrl.openConnection();
			connection.setRequestProperty("accept", "*/*");
			connection.setRequestProperty("connection", "Keep-Alive");
			connection.setRequestProperty("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1)");
			connection.connect();
			in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
			String line;
			while ((line = in.readLine()) != null) {

				result += line;
			}
		} catch (Exception e) {
			System.out.println("发送GET请求出现异常！" + e);
			e.printStackTrace();
		}
		finally {
			try {
				if (in != null) {
					in.close();
				}
			} catch (Exception e2) {
				e2.printStackTrace();
			}
		}
		return result;
	}

	/**
	 * 向指定 URL 发送POST方法的请求
	 * 
	 * @param url   发送请求的 URL
	 * @param param 请求参数，请求参数应该是 JSONObject.toJSONString(param) 的形式。
	 * @return 所代表远程资源的响应结果
	 */
	public static String sendPost(String url, String param) {
		PrintWriter out = null;
		BufferedReader in = null;
		String result = "";
		try {
			URL realUrl = new URL(url);
			// 打开和URL之间的连接
			URLConnection conn = realUrl.openConnection();
			// 设置通用的请求属性
			conn.setRequestProperty("accept", "*/*");
			conn.setRequestProperty("connection", "Keep-Alive");
			conn.setRequestProperty("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1)");
			conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
			// 发送POST请求必须设置如下两行
			conn.setDoOutput(true);
			conn.setDoInput(true);
			// 获取URLConnection对象对应的输出流
			out = new PrintWriter(conn.getOutputStream());
			// 发送请求参数
			out.print(param);
			// flush输出流的缓冲
			out.flush();
			// 定义BufferedReader输入流来读取URL的响应
			in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
			String line;
			while ((line = in.readLine()) != null) {
				result += line;
			}
		} catch (Exception e) {
			System.out.println("发送 POST 请求出现异常！" + e);
			e.printStackTrace();
		}
		// 使用finally块来关闭输出流、输入流
		finally {
			try {
				if (out != null) {
					out.close();
				}
				if (in != null) {
					in.close();
				}
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}
		return result;
	}

	public static String sendPostEC(String url, String param) {
		PrintWriter out = null;
		BufferedReader in = null;
		String result = "";
		try {
			String urlNameString = url + "?" + param;
			System.out.println(urlNameString);
			URL realUrl = new URL(urlNameString);

			// 打开和URL之间的连接
			URLConnection conn = realUrl.openConnection();
			// 设置通用的请求属性
			conn.setRequestProperty("accept", "*/*");
			conn.setRequestProperty("connection", "Keep-Alive");
			conn.setRequestProperty("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1)");
			conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
			// 发送POST请求必须设置如下两行
			conn.setDoOutput(true);
			conn.setDoInput(true);
			// 获取URLConnection对象对应的输出流
			out = new PrintWriter(conn.getOutputStream());
			// 发送请求参数
			out.print(param);
			// flush输出流的缓冲
			out.flush();
			// 定义BufferedReader输入流来读取URL的响应
			in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
			String line;
			while ((line = in.readLine()) != null) {
				result += line;
			}
			// createJsonFile(result,"EC0624-1.json");
		} catch (Exception e) {
			System.out.println("发送 POST 请求出现异常！" + e);
			e.printStackTrace();
		}
		// 使用finally块来关闭输出流、输入流
		finally {
			try {
				if (out != null) {
					out.close();
				}
				if (in != null) {
					in.close();
				}
			} catch (IOException ex) {
				ex.printStackTrace();
			}
		}
		return result;
	}

	public static List<File> getCSV(String DirPath) throws IOException {

		// 获取存放文件的目录
		File dirpath = new File(DirPath);
		// 将该目录下的所有文件放置在一个File类型的数组中
		File[] filelist = dirpath.listFiles();

		// 创建一个空的file类型的list集合，用于存放符合条件的文件
		List<File> newfilelist = new ArrayList<>();
		// 遍历filelist，如果是文件则存储在新建的list集合中
		for (File file : filelist) {
			if (file.isFile()) {
				newfilelist.add(file);
			}
		}
		return newfilelist;


	}

}
