clc
clear


% This script is used for: (1) Mapping ignition probability (2) Get the
% corresponding FMC values


%***************INPUT PARAMETERS********
% (1) IP_FMC=1 get ip; IP_FMC=2 get fmc transform nc to FMC
IP_FMC=1   ;



% (3) Path to the original NC file
LFMCdatadir='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/FMC_Product_using_MCD12Q1/';

% (4) Path to the vegetation type
Vegdatadir='/g/data/xc0/original/landcover/aus/Landcover_AU_merged_each_scene_MCD12Q2_2001-2013/';

% (5) path to the mcd64a1 burned product
% Burntdatadir=[root_path '\S_research_program\G. Mapping LFMC for AU\II. method\Scriptd_for_Logstic\Data\MCD64A1\'];

% (6) Path to the meanlfmc
MeanLFMCdatadir='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/Anomaly_Mean_FMC_MCD12Q1/';

% (7) Path to the geoinfor
geofileName='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/Geoinfor_each_scene_MCD12Q1/';

% (8) Path to Output
Outputdir='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/Flammability index product/';

%**************END*************************



% MAIN SCRIPT
% (1) get batch LFMC NC files
LFMCfilelist=dir([LFMCdatadir,'*.nc']);
k1=length(LFMCfilelist);
LFMCname_year=zeros(k1,1);
LFMCname_doy=zeros(k1,1);
LFMCname_hv=zeros(k1,1);
LFMCname_date=zeros(k1,1);
for i=1:k1
    LFMCname_year(i)=str2double(LFMCfilelist(i).name(10:13));
    LFMCname_doy(i)=str2double(LFMCfilelist(i).name(14:16));
    LFMCname_date(i)=str2double(LFMCfilelist(i).name(10:16));
    LFMCname_hv(i)=str2double(LFMCfilelist(i).name(19:20))*1000+str2double(LFMCfilelist(i).name(22:23));
end

% (2) get the batch vegetation type
% Vegdatadir='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/Landcover_for_eachscene/';
Vegfilelist=dir([Vegdatadir,'*.tif']);
k2=length(Vegfilelist);
Vegname_year=zeros(k2,1);
Vegname_hv=zeros(k2,1);
for i=1:k2
    Vegname_year(i)=str2double(Vegfilelist(i).name(21:24));
    Vegname_hv(i)=str2double(Vegfilelist(i).name(33:34))*1000+str2double(Vegfilelist(i).name(36:37));
end

% (3) Get the batch burnt area
% Burntdatadir='/g/data/xc0/project/FMC_Australia/FMC_PRODUCTS_AU/TEMP/';
% Burntfilelist=dir([Burntdatadir,'*.hdf']);
% k3=length(Burntfilelist);

% (4) Get the mean LFMC dataset
% Burntdatadir='F:\S_research_program\G. Mapping LFMC for AU\II. method\Scriptd_for_Logstic\Data\MCD64A1\';
MeanLFMCfilelist=dir([MeanLFMCdatadir,'*.txt']);
k4=length(MeanLFMCfilelist);
MeanLFMC_hv=zeros(k4,1);
MeanLFMC_doy=zeros(k4,1);
for i=1:k4
    MeanLFMC_hv(i,1)=str2double(MeanLFMCfilelist(i).name(15:16))*1000+str2double(MeanLFMCfilelist(i).name(18:19));
    MeanLFMC_doy(i,1)=str2double(MeanLFMCfilelist(i).name(10:12));
end

%(5) path to the geinfor file
%get the coordinate system from the original file
geoinforlist=dir([geofileName,'*.tif']);
k5=length(geoinforlist);
geoinfor_hv=zeros(k5,1);
for i=1:k5
    if length(geoinforlist(i).name)~=28
        continue;
    end
    geoinfor_hv(i)=str2double(geoinforlist(i).name(15:16))*1000+str2double(geoinforlist(i).name(18:19));
end




for i=1:k1
    lefti=k1-i
    
    %     %open NC file  i-2
    %     filename_LFMC_16days=[LFMCdatadir,LFMCfilelist(i-2).name];
    %     ncid2=netcdf.open(filename_LFMC_16days,'NC_NOWRITE');
    %     LFMCMeanData_16days= ncread(filename_LFMC_16days,'lfmc_mean'); % get the specific variable for NC file
    %     LFMCMeanData_16days=LFMCMeanData_16days';
    
    %open NC file  i
    date_targetday=LFMCname_date(i);
    hv_target=LFMCname_hv(i);
    IP=zeros(2400);
    if IP_FMC==1
        str16day=num2str(date_targetday);
        lfmc_index_16day=find((date_targetday-LFMCname_date==16|(date_targetday-LFMCname_date==648)|((date_targetday-LFMCname_date==640)...
            &strcmp(str16day(5:7),'009')==1))&(hv_target==LFMCname_hv));
        
        if isempty(lfmc_index_16day)==1
            continue;
        end
        
        lfmc_index=find((date_targetday-LFMCname_date==8|(date_targetday-LFMCname_date==640))&(hv_target==LFMCname_hv));
        
        if isempty(lfmc_index)==1
            continue;
        end
        
        %open nc file t-2
        filename_LFMC_16days=[LFMCdatadir,LFMCfilelist(lfmc_index_16day(1)).name];
        ncid2=netcdf.open(filename_LFMC_16days,'NC_NOWRITE');
        LFMCMeanData_16days= ncread(filename_LFMC_16days,'lfmc_mean'); % get the specific variable for NC file
        LFMCMeanData_16days=LFMCMeanData_16days';
        

        %open NC file  t-1
        filename_LFMC_8days=[LFMCdatadir,LFMCfilelist(lfmc_index(1)).name];
        ncid1=netcdf.open(filename_LFMC_8days,'NC_NOWRITE');
        LFMCMeanData_8days= ncread(filename_LFMC_8days,'lfmc_mean'); % get the specific variable for NC file
        LFMCMeanData_8days=LFMCMeanData_8days';
        
        diff=LFMCMeanData_16days-LFMCMeanData_8days;
        
        %open landcover map
        Match_Veg= find((LFMCname_hv(lfmc_index(1))==Vegname_hv)&(Vegname_year==LFMCname_year(lfmc_index(1))));
        if isempty(Match_Veg)==1
            continue;
        end
        
        filename_veg=[Vegdatadir,Vegfilelist(Match_Veg(1)).name];
        data_veg=imread(filename_veg);
        %         data_veg=data_veg';
        %open meanlfmc
        MatchMeanLFMC_hv_index=find(MeanLFMC_hv==LFMCname_hv(lfmc_index(1))&LFMCname_doy(lfmc_index(1))==MeanLFMC_doy);
        if isempty(MatchMeanLFMC_hv_index)==1
            continue;
        end
        MeanLFMC_dataset=importdata([MeanLFMCdatadir,MeanLFMCfilelist(MatchMeanLFMC_hv_index(1)).name]);
        MeanLFMC_dataset=MeanLFMC_dataset';
        %for grassland
        num_grassland=find((data_veg==1)&(LFMCMeanData_8days>0)&(LFMCMeanData_8days<400)&...
            (MeanLFMC_dataset>0)&(MeanLFMC_dataset<4000)&diff<400);
        grassland_anomaly=LFMCMeanData_8days(num_grassland)./MeanLFMC_dataset(num_grassland);
        IP(num_grassland)=1./(1+exp(-0.18+0.001.*LFMCMeanData_8days(num_grassland)-0.024.*diff(num_grassland)...
            +0.024.*grassland_anomaly));
        
        %for shrubland
        num_shrubland=find(data_veg==2&(LFMCMeanData_8days>0)&(LFMCMeanData_8days<400)&...
            (MeanLFMC_dataset>0)&(MeanLFMC_dataset<4000)&diff<400);
        shrubland_anomaly=LFMCMeanData_8days(num_shrubland)./MeanLFMC_dataset(num_shrubland);
        IP(num_shrubland)=1./(1+exp(-5.6552+0.0911.*LFMCMeanData_8days(num_shrubland)-0.0047.*diff(num_shrubland)...
            +0.2845.*shrubland_anomaly));
        
        %for forest
        num_forest=find(data_veg==3&(LFMCMeanData_8days>0)&(LFMCMeanData_8days<400)&...
            (MeanLFMC_dataset>0)&(MeanLFMC_dataset<4000)&diff<400);
        forest_anomaly=LFMCMeanData_8days(num_forest)./MeanLFMC_dataset(num_forest);
        IP(num_forest)=1./(1+exp(-1.5145+0.0251.*LFMCMeanData_8days(num_forest)+0.0245.*diff(num_forest)...
            +0.0187.*forest_anomaly));
        
        resu_path=strcat(Outputdir,'FI_',LFMCfilelist(i).name(10:16),'_',LFMCfilelist(i).name(18:23),'.tif');
        
        geoinforindex=find(LFMCname_hv(lfmc_index(1))==geoinfor_hv);
        if isempty(geoinforindex)==1
            continue;
        end
        [tempImage, geoR]=geotiffread([geofileName geoinforlist(geoinforindex(1)).name]);
        geoInfo=geotiffinfo([geofileName geoinforlist(geoinforindex(1)).name]);
        
        geotiffwrite(resu_path,IP, geoR,'GeoKeyDirectoryTag', geoInfo.GeoTIFFTags.GeoKeyDirectoryTag);
        netcdf.close(ncid1);
        netcdf.close(ncid2);
    else
        filename_LFMC=[LFMCdatadir,LFMCfilelist(i).name];
        ncid=netcdf.open(filename_LFMC,'NC_NOWRITE');
        LFMCMeanData= ncread(filename_LFMC,'lfmc_mean'); % get the specific variable for NC file
        LFMCMeanData=LFMCMeanData';
        
        resu_path=strcat(Outputdir,'FMC_',LFMCfilelist(i).name(10:16),'_',LFMCfilelist(i).name(18:23),'.tif');
        
        geoinforindex=find(LFMCname_hv(i)==geoinfor_hv);
        if isempty(geoinforindex)==1
            continue;
        end
        [tempImage, geoR]=geotiffread([geofileName geoinforlist(geoinforindex(1)).name]);
        geoInfo=geotiffinfo([geofileName geoinforlist(geoinforindex(1)).name]);
        
        geotiffwrite(resu_path,LFMCMeanData, geoR,'GeoKeyDirectoryTag', geoInfo.GeoTIFFTags.GeoKeyDirectoryTag);
        netcdf.close(ncid);
    end
    
    %     netcdf.close(ncid2);
end







