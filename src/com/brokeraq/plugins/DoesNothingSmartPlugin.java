package com.brokeraq.plugins;

import com.activequant.aqviz.BluntConsole;
import com.activequant.interfaces.aqviz.IPlugin;

public class DoesNothingSmartPlugin implements IPlugin {

	BluntConsole bc = new BluntConsole("NothingSmartPlugin");

	@Override
	public void initialize() throws Exception {
		bc.addLog("Initialized.");
	}

}
