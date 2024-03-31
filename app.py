import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from Summerize import transcribe, detect_language, translate_large_text, recursive_summarize, summarize_paragraph, identify_key_phrases, highlight_key_phrases
import re
#from  import Server

def main():
    st.title("Video Summarizer Tool")

    # Input box for users to input the URL
    videourl = st.text_input("Enter YouTube Video URL:")
    videoid = videourl.split("/")[-1]


    if st.button("Process Video"):
        st.info("Processing video... This may take some time.")

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(videoid)
            all_languages = ["hi", "bn", "te", "ta", "mr", "en", "es", "fr", "de", "zh-Hans", 'ar']

            total_content = ''
            for transcript in transcript_list:
                if transcript.language_code in all_languages:
                    captions = transcript.fetch()
                    for segment in captions:
                        if segment['text'] != '':  # Skip empty segments
                            total_content += segment['text'] + ' '
            
            detected_language = detect_language(total_content)

            if detected_language:
                st.success(f"The detected language is: {detected_language}")
                if detected_language != 'en':
                    total_content = translate_large_text(total_content, src_language=detected_language)
                    st.success(f"Translated text to English 👍🏻")

            # Transcribe the video if no transcript is available
            if not total_content:
                total_content = transcribe(videourl)
                st.success(f"Transcribed text:\n{total_content}")

            st.subheader("Summarization and Key Phrases Extraction")
            
            all_summaries = recursive_summarize(total_content)
           
            def expandable_button(summary, button_label):
                button_expander = st.expander(button_label)
                with button_expander:
                    st.write(summary)
            

            if all_summaries:
                for i, summary in enumerate(all_summaries):
                    summary = re.sub(r'\b(?:Summarize|Summarizing|Summarized|summarize|summarizing|summarized|Summerize:)\b', '', summary)
                    all_summaries[i] = summary
                    expandable_button(summary, f"Summary {i+1}  approx words: {round(len(summary.split(' '))/100)*100}")

            result = summarize_paragraph(all_summaries[-1], num_sentences=5)
            key_phrases = identify_key_phrases(all_summaries[-1], min_length=2, max_length=4)

            if key_phrases is not None:
                st.subheader("Key Phrases:")
                st.text(', '.join(key_phrases))

                st.subheader("Highlighted Summary:")
                for i, sentence in enumerate(result, 1):
                    st.write(f"{i}. {highlight_key_phrases(sentence, key_phrases)}",unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
