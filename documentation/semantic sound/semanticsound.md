# Semantic Sound Documentation

This section discusses the methodology behing the semantic sound data sonification schemata, implemented in the [pure data patches](https://github.com/danhearn/transforming-collections/tree/pure-data/Pure%20Data). There are 2 separate channels: museum and archive. 

## Museum

Trained a Machine Learning (ML) algorithm on field recordings recorded within archival spaces at the Tate Modern. These sounds were fed into a [Realtime Audio Variational autoEncoder (RAVE)](https://github.com/acids-ircam/RAVE) developed by [IRCAM](https://www.ircam.fr) - this neural network learns to re-synthesise the sounds, artificially, in real-time. The model learns a compressed, low-dimensional representation of the high-dimensional audio input. This compressed "manifold" can be explored through exploration of the ["latent space"](https://samanemami.medium.com/a-comprehensive-guide-to-latent-space-9ae7f72bdb2f#:~:text=Latent%20space%20is%20a%20lower,a%20specific%20feature%20or%20characteristic.) - movement within this space will modify the audio output, corresponding to different learned representations of the archival training data. For example, one region within the latent space could correspond to the background chatter of voices. This latent space is explored, and semantically meaningful movements can be automated.

The Museum model takes a 5-dimensional input corresponding to the vectorised keywords tied to the current work. This vector modulates spatial position in the latent space - this modulation is aleatoric in nature but constrained by the semantically meaningful regions recorded in the exploration phase. This creates a generative soundscape, constantly changing, yet supporting the conceptual framework of the artwork. Through this methodology, archival sonification feeds back into the museum collection. 

## The Ancestors 

The Ancestors side utilizes live recordings of instruments played around Tate Britain, which are processed through a custom granular synthesizer developed by GitHub user jaffasplaffa (https://github.com/jaffasplaffa/Pure-data-patches). Granular synthesis is a method of sound design that breaks an audio sample into tiny fragments, or "grains", typically ranging from 1ms to 100ms in length. Each grain can be independently manipulated—adjusting its timing, speed, phase, and frequency—allowing for a dynamic and textured reshaping of the original sound.

For the data sonification process, incoming vectors are mapped to four key parameters within the granular synthesizer. One of these is the randomization of grain position, which determines the extent to which grains are played back in a different sequence from the original recording, creating a unique reordering of time. Other modulated parameters include grain phase, speed, and reverse playback. Together, these variations create a constantly evolving soundscape.



