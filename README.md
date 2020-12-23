# tracktrace

tracktrace allows you to track shipping containers across all major shipping lines as well as [Class 1](https://en.wikipedia.org/wiki/Railroad_classes#Class_I) North American railways.

Major steamship lines all have container tracking on their websites and/or apps.

### Ocean


| Steamship Line   |SCAC | Supported     | Container Tracking Website |
| -------------    | :---------: | :-------------: | :---------------: |
| Alianca          | ANRM |   Yes            | [Link](https://www.alianca.com.br/alianca/en/alianca/ecommerce_alianca/track_trace_alianca/index.html)  |
| APL              | APLU |   Yes            | [Link](https://www.apl.com/ebusiness/tracking)  |
| Arkas Container Transport |ARKU | Not yet     | [Link](https://webtracking.arkasline.com.tr/shipmenttracking)
| CMA CGM          | CMDU |   Yes            | [Link](https://www.cma-cgm.com/ebusiness/tracking)  |
| Cosco            | COSU |   Partially            | [Link](https://elines.coscoshipping.com/ebusiness/cargoTracking)  |
| Evergreen        | EGLV |   Not yet            | [Link](https://www.shipmentlink.com/servlet/TDB1_CargoTracking.do)  |
| Hamburg SUD      | SUDU |   Yes            | [Link](https://www.hamburgsud-line.com/liner/en/liner_services/ecommerce/track_trace/index.html)  |
| Hapag Lloyd      | HLCU |   Yes       | [Link](https://www.hapag-lloyd.com/en/online-business/tracing/tracing-by-container.html)  |
| Hyundai Merchant Marine (HMM) |HDMU | Not yet | [Link](https://www.hmm21.com/cms/business/ebiz/trackTrace/trackTrace/index.jsp)
| Maersk           | MAEU |   Partially            | [Link](https://www.maersk.com/tracking/)  |
| Matson           | MATS   | Not yet       | [Link](https://www.matson.com/shipment-tracking.html)
| Mediterranean Shipping Company (MSC) |MSCU |  Yes     | [Link](https://www.msc.com/track-a-shipment?agencyPath=mwi) |
| ONE Line         | ONEY |   Yes            | [Link](https://ecomm.one-line.com/ecom/CUP_HOM_3301.do)  |
| Orient Overseas Container Line (OOCL) | OOLU | Not yet | [Link](https://www.oocl.com/eng/ourservices/eservices/cargotracking/Pages/cargotracking.aspx)
| Pacific International Lines (PIL) | PCIU | Not yet | [Link](https://www.pilship.com/en--/120.html)|
| Wan Hai Lines | WHLC | Not yet | [Link](https://www.wanhai.com/views/cargoTrack/CargoTrack.xhtml)
| Yang Ming        |YMLU |   Not yet            | [Link](https://www.yangming.com/e-service/Track_Trace/track_trace_cargo_tracking.aspx)    |
| Zim Integrated Shipping Services (ZIM) |ZIMU | Not yet | [Link](https://www.zim.com/tools/track-a-shipment)|


### Rail

Railroads often require an account to track containers. At certain railroads, you also need to be a Notify Party to access tracking information. 

For example, BNSF doesn't show any tracking information if your company is not a Notify Party. UP, on the other hand, shows partial tracking information. 


| Railroad | Supported | Need Account | Need to be a Notify Party |
| ---- | :--: | :-------: | :---------: | 
| BNSF Railway (BNSF) | Not yet | Yes | Yes |
| Canadian National Railway (CN) | Not yet | Yes | Don't know | 
| Canadian Pacific Railway (CPR) | Not yet | Yes | Don't know |
| CSX Transportation (CSX) | Yes | No | No | 
| Ferromex | Not yet | Yes | Don't know | 
| Kansas City Southern Railway (KCS)| Not yet | Yes | Don't know | 
| Norfolk Southern Railway (NS) | Yes | Yes | No |
| Union Pacific Railway (UP) | Partially | Yes | No | 



## Installation


```sh
#TODO (not on pypi yet)
pip install tracktrace 
```

## Usage example


```python
from tracktrace import ocean

con = ocean.container.create("MSCU", "MEDU3288655")

```


## Release History

* 0.0.1
    * Work in progress

## Meta

Dhruv Kar – [dhruvkar](https://twitter.com/dhruvkar) – dhruv@wints.org

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/dhruvkar/](https://github.com/dhruvkar/)

## Contributing

1. Fork it (<https://github.com/dhruvkar/tracktrace/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

