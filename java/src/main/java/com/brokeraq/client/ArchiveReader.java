/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.brokeraq.client;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;

import com.activequant.archive.MultiValueTimeSeriesIterator;
import com.activequant.domainmodel.TimeFrame;
import com.activequant.domainmodel.TimeStamp;
import com.activequant.domainmodel.Tuple;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Fetches historical data from the archive.
 *
 * @author ustaudinger
 */
public class ArchiveReader {

    private TimeFrame timeFrame;
    private String baseUrl = "http://78.47.96.150:44444/csv/";
    private static final Logger log = Logger.getLogger(ArchiveReader.class.getCanonicalName());

    public ArchiveReader(TimeFrame timeFrame) {
        this.timeFrame = timeFrame;

    }

    /**
     * dirty hack, just takes open, high,low,close, volumne for now. Need to
     * think about a way to link AQMS and this piece together. Maybe through
     * some additional parameter that tells AQMS to always include field names
     * for every row ... or something like that.
     *
     */
    public MultiValueTimeSeriesIterator getMultiValueStream(String streamId,
            TimeStamp startTimeStamp, TimeStamp stopTimeStamp) throws Exception {
        LocalIter li = new LocalIter(streamId, startTimeStamp, stopTimeStamp);
        return li;
    }

    class LocalIter extends MultiValueTimeSeriesIterator {

        private String nextLine = null;
        private final BufferedReader br;

        public LocalIter(String streamId,
                TimeStamp startTimeStamp, TimeStamp stopTimeStamp) throws IOException {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd");
            final String url = baseUrl + "?SERIESID=" + streamId + "&FREQ=" + timeFrame.toString() + "&FIELD=O,H,L,C,V&STARTDATE=" + sdf.format(startTimeStamp.getCalendar().getTime()) + "&ENDDATE=" + sdf.format(stopTimeStamp.getCalendar().getTime());
            log.log(Level.INFO, "Using url: {0}", url);
            // let's read from this url ... 
            URL u = new URL(url);
            InputStream inStream = u.openStream();
            br = new BufferedReader(new InputStreamReader(inStream));
            // skip the header. 
            br.readLine();
            // read the first line. 
            nextLine = br.readLine();
        }

        @Override
        public boolean hasNext() {
            return nextLine != null;
        }

        /**
         * The iterator's next implementation will return a tuple of timestamp
         * and field map.
         *
         */
        @Override
        public Tuple<TimeStamp, Map<String, Double>> next() {
            if (nextLine != null) {

                // let's parse the line. 
                String[] s = nextLine.split(",");
                // 
                Double open = s[2] == null ? Double.NaN : Double.parseDouble(s[2]);
                Double high = s[3] == null ? Double.NaN : Double.parseDouble(s[3]);
                Double low = s[4] == null ? Double.NaN : Double.parseDouble(s[4]);
                Double close = s[5] == null ? Double.NaN : Double.parseDouble(s[5]);
                // 
                TimeStamp ts = new TimeStamp(Long.parseLong(s[0]));
                Map<String, Double> m = new HashMap<String, Double>();
                m.put("O", open);
                m.put("H", high);
                m.put("L", low);
                m.put("C", close);
                m.put("V", 0.0);
                Tuple<TimeStamp, Map<String, Double>> t = new Tuple<TimeStamp, Map<String, Double>>();
                t.setA(ts);
                t.setB(m);
                // 
                try {
                    nextLine = br.readLine();
                } catch (IOException e) {
                    nextLine = null;
                    e.printStackTrace();
                }
                return t;

            } else {
                // end of stream.
                return null;
            }
        }
    }
}
