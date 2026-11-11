#include <windows.h>
#include <wmsdk.h>
#include <nserror.h>
#include <fcntl.h>
#include <io.h>
#include <cstdio>
#include <cstdlib>
#include <vector>

static void check(HRESULT result, const char *step) {
    if (FAILED(result)) { fprintf(stderr,"%s: %08lx\n",step,(unsigned long)result); exit(1); }
}
int wmain(int argc,wchar_t **argv) {
    if (argc < 4) return 2;
    FILE *timestamps=_wfopen(argv[3],L"rb");
    if(!timestamps)return 2;
    _setmode(_fileno(stdin),_O_BINARY);
    check(CoInitializeEx(nullptr,COINIT_MULTITHREADED),"COM");
    auto dll=LoadLibraryExW(L"wmvcore.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
    if(!dll)return 3;
    auto makeReader=(decltype(&WMCreateSyncReader))GetProcAddress(dll,"WMCreateSyncReader");
    auto makeWriter=(decltype(&WMCreateWriter))GetProcAddress(dll,"WMCreateWriter");
    IWMSyncReader *reader=nullptr;
    check(makeReader(nullptr,0,&reader),"reader");
    check(reader->Open(argv[1]),"open original");
    IWMProfile *profile=nullptr;
    check(reader->QueryInterface(IID_PPV_ARGS(&profile)),"source profile");
    IWMWriter *writer=nullptr;
    check(makeWriter(nullptr,&writer),"writer");
    check(writer->SetProfile(profile),"reuse original encoding profile");
    IWMWriterAdvanced *advanced=nullptr;
    check(writer->QueryInterface(IID_PPV_ARGS(&advanced)),"writer advanced");
    DWORD count=0,video=0;
    WORD audioStream=0;
    check(writer->GetInputCount(&count),"inputs");
    for (DWORD i=0;i<count;i++) {
        IWMInputMediaProps *props=nullptr;
        check(writer->GetInputProps(i,&props),"input");
        GUID type={};check(props->GetType(&type),"input type");
        if (type==WMMEDIATYPE_Audio) {
            check(writer->SetInputProps(i,nullptr),"compressed audio");
            check(reader->GetStreamNumberForOutput(i,&audioStream),"audio stream");
            check(reader->SetReadStreamSamples(audioStream,TRUE),"audio passthrough");
        } else if (type==WMMEDIATYPE_Video) {
            video=i; DWORD formats=0;bool found=false;
            check(writer->GetInputFormatCount(i,&formats),"formats");
            for(DWORD j=0;j<formats&&!found;j++) {
                IWMInputMediaProps *fmt=nullptr;check(writer->GetInputFormat(i,j,&fmt),"format");
                DWORD bytes=0;check(fmt->GetMediaType(nullptr,&bytes),"size");
                std::vector<BYTE> buf(bytes);
                auto mt=(WM_MEDIA_TYPE*)buf.data();check(fmt->GetMediaType(mt,&bytes),"media type");
                if(mt->subtype==WMMEDIASUBTYPE_I420 || mt->subtype.Data1==0x56555949) {
                    check(writer->SetInputProps(i,fmt),"raw YUV420");found=true;
                }
                fmt->Release();
            }
            if(!found){fprintf(stderr,"no I420 input\n");return 4;}
        }
        props->Release();
    }
    if(!audioStream || count!=2)return 5;
    check(writer->SetOutputFilename(argv[2]),"output");
    check(writer->BeginWriting(),"begin");
    INSSBuffer *sound=nullptr;
    QWORD soundTime=0,duration=0;DWORD flags=0;
    bool audioEnd=false;
    auto feedAudio=[&](QWORD until) {
        while(!audioEnd) {
            if(!sound) {
                HRESULT hr=reader->GetNextSample(audioStream,&sound,&soundTime,&duration,&flags,nullptr,nullptr);
                if(hr==NS_E_NO_MORE_SAMPLES){audioEnd=true;break;}
                check(hr,"read source audio");
            }
            if(soundTime>until)break;
            check(advanced->WriteStreamSample(audioStream,soundTime,0,duration,flags,sound),"write source audio");
            sound->Release();sound=nullptr;
        }
    };
    const DWORD size=1920*1080*3/2;
    unsigned n=0;
    for(;;) {
        INSSBuffer *frame=nullptr;
        check(writer->AllocateSample(size,&frame),"frame buffer");
        BYTE *pixels=nullptr;check(frame->GetBuffer(&pixels),"pixels");
        size_t received=fread(pixels,1,size,stdin);
        if(!received){frame->Release();break;}
        if(received!=size){fprintf(stderr,"partial video frame\n");return 6;}
        QWORD time=0;
        if(fread(&time,sizeof(time),1,timestamps)!=1)return 8;
        feedAudio(time);
        check(frame->SetLength(size),"frame length");
        check(writer->WriteSample(video,time,0,frame),"encode frame");
        frame->Release();n++;
    }
    fclose(timestamps);
    if(argc<5)feedAudio(~QWORD(0));
    check(writer->EndWriting(),"finish");
    fprintf(stderr,"Encoded %u frames using original Windows Media profile\n",n);
    advanced->Release();writer->Release();profile->Release();reader->Close();reader->Release();
    CoUninitialize();
    return n==0;
}
