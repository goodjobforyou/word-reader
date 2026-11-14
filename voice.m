#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
static NSArray *jobs;
static NSString *folder;
static NSUInteger indexOfJob = 0;
static AVSpeechSynthesizer *synth;
static AVSpeechSynthesisVoice *voice;
static AVSpeechSynthesisVoice *femaleVoice;
static AVAudioFile *file;
static NSUInteger finishedIndex = 999999;
static void nextJob(void);
static void completeJob(void) {
    if (finishedIndex == indexOfJob) return;
    finishedIndex = indexOfJob;
    file = nil;
    printf("%s\n",[jobs[indexOfJob][@"id"] UTF8String]); fflush(stdout);
    indexOfJob++;
    dispatch_async(dispatch_get_main_queue(), ^{nextJob();});
}
@interface SpeechDelegate : NSObject<AVSpeechSynthesizerDelegate>
@end
@implementation SpeechDelegate
- (void)speechSynthesizer:(AVSpeechSynthesizer *)s didFinishSpeechUtterance:(AVSpeechUtterance *)u { completeJob(); }
@end
static SpeechDelegate *delegate;
static void nextJob(void) {
    if (indexOfJob >= jobs.count) exit(0);
    NSDictionary *job = jobs[indexOfJob];
    AVSpeechUtterance *utterance;
    if ([job[@"ipa"] isKindOfClass:NSString.class]) {
        // The platform ignores IPA U+0261 and misreads U+025C in this voice.
        // Preserve displayed textbook IPA; adapt only the synthesis input.
        NSString *ipa=[job[@"ipa"] stringByReplacingOccurrencesOfString:@"ɡ" withString:@"g"];
        NSDictionary *nurse=@{@"ɜː":@"err",@"bɜː":@"burr",@"wɜːld":@"world"};
        if (nurse[ipa]) utterance=[[AVSpeechUtterance alloc] initWithString:nurse[ipa]];
        else {
            NSAttributedString *text = [[NSAttributedString alloc] initWithString:job[@"text"] attributes:@{AVSpeechSynthesisIPANotationAttribute:ipa}];
            utterance = [[AVSpeechUtterance alloc] initWithAttributedString:text];
        }
    } else { utterance = [[AVSpeechUtterance alloc] initWithString:job[@"text"]]; }
    utterance.voice = [job[@"voice"] isEqualToString:@"female"] ? femaleVoice : voice;
    utterance.rate = 0.44;
    file = nil;
    [synth writeUtterance:utterance toBufferCallback:^(AVAudioBuffer *buffer) {
        AVAudioPCMBuffer *pcm = (AVAudioPCMBuffer *)buffer;
        if (pcm.frameLength == 0) {
            return;
        }
        NSError *error=nil;
        if (!file) {
            NSURL *url=[NSURL fileURLWithPath:[folder stringByAppendingPathComponent:[job[@"id"] stringByAppendingString:@".wav"]]];
            file=[[AVAudioFile alloc] initForWriting:url settings:pcm.format.settings error:&error];
        }
        if (error || ![file writeFromBuffer:pcm error:&error]) { fprintf(stderr,"Audio failed\n"); exit(1); }
    }];
}
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        jobs=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[1])] options:0 error:nil];
        folder=@(argv[2]);
        synth=[AVSpeechSynthesizer new];
        delegate=[SpeechDelegate new]; synth.delegate=delegate;
        for (AVSpeechSynthesisVoice *candidate in AVSpeechSynthesisVoice.speechVoices) {
            if (![candidate.language isEqualToString:@"en-GB"]) continue;
            if ([candidate.name isEqualToString:@"Daniel"]) voice=candidate;
            if ([candidate.name hasPrefix:@"Flo"]) femaleVoice=candidate;
        }
        if (!voice) voice=[AVSpeechSynthesisVoice voiceWithLanguage:@"en-GB"];
        if (!jobs || !voice || !femaleVoice) {fprintf(stderr,"British voices unavailable\n");return 1;}
        nextJob();
        [[NSRunLoop mainRunLoop] run];
    }
    return 0;
}
