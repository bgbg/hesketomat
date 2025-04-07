'use client'

import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Input,
  Button,
  Card,
  CardBody,
  Image,
  Text,
  Stack,
  Heading,
  Table,
  Tbody,
  Tr,
  Td,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  useToast,
  ButtonGroup,
  Highlight,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  HStack,
  Flex,
} from '@chakra-ui/react'
import useSWR, { mutate } from 'swr'
import { podcastsApi, episodesApi, type PodcastWithCount, type SearchResult } from '../lib/api'

export default function EpisodesTab() {
  const [selectedPodcasts, setSelectedPodcasts] = useState<number[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [titleWeight, setTitleWeight] = useState(50)
  const [descriptionWeight, setDescriptionWeight] = useState(50)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const toast = useToast()

  const { data, error, isLoading } = useSWR<PodcastWithCount[]>(
    '/podcasts/with_counts',
    () => podcastsApi.getAllWithCounts(),
    {
      onError: (err) => {
        console.error('SWR Error in EpisodesTab:', err)
        toast({
          title: 'שגיאה',
          description: err.message || 'שגיאה בטעינת ההסכתים',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }
  )
  const podcasts = data || []

  // Select all podcasts by default when data loads
  useEffect(() => {
    if (data && data.length > 0) {
      setSelectedPodcasts(data.map(podcast => podcast.id))
    }
  }, [data])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (selectedPodcasts.length > 0) {
        performSearch()
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery, titleWeight, descriptionWeight, selectedPodcasts])

  const performSearch = async () => {
    if (selectedPodcasts.length === 0) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    try {
      const results = await episodesApi.search(
        searchQuery.trim(),
        selectedPodcasts,
        { title_weight: titleWeight, description_weight: descriptionWeight }
      )
      setSearchResults(results)
    } catch (error: any) {
      toast({
        title: 'שגיאה',
        description: error.message || 'שגיאה בחיפוש',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleRefresh = async () => {
    if (selectedPodcasts.length === 0) {
      toast({
        title: 'שגיאה',
        description: 'נא לבחור הסכת אחד לפחות',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      // Refresh each selected podcast
      await Promise.all(selectedPodcasts.map(id => podcastsApi.refresh(id)))

      // Refresh the podcasts list to get updated counts
      await mutate('/podcasts/with_counts')

      // Refresh the search results if there's an active search
      if (searchQuery.trim()) {
        await performSearch()
      }

      toast({
        title: 'הצלחה',
        description: 'הפרקים עודכנו בהצלחה',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      toast({
        title: 'שגיאה',
        description: error.message || 'שגיאה בעדכון הפרקים',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleEmpty = async () => {
    if (selectedPodcasts.length === 0) {
      toast({
        title: 'שגיאה',
        description: 'נא לבחור הסכת אחד לפחות',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    try {
      await episodesApi.delete(selectedPodcasts)
      setSearchResults([])
      await mutate('/podcasts/with_counts')
      toast({
        title: 'הצלחה',
        description: 'הפרקים נמחקו בהצלחה',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      toast({
        title: 'שגיאה',
        description: error.message || 'שגיאה במחיקת הפרקים',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url)
    toast({
      title: 'הצלחה',
      description: 'הקישור הועתק ללוח',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const sanitizeText = (text: string) => {
    // Remove HTML tags and decode HTML entities
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = text
    return tempDiv.textContent || tempDiv.innerText || ''
  }

  const highlightText = (text: string, matches: [number, number][] | undefined) => {
    if (!matches || matches.length === 0) return sanitizeText(text)

    const sanitizedText = sanitizeText(text)
    let result = ''
    let lastEnd = 0

    matches.forEach(([start, end]) => {
      result += sanitizedText.slice(lastEnd, start)
      result += `<mark>${sanitizedText.slice(start, end)}</mark>`
      lastEnd = end
    })

    result += sanitizedText.slice(lastEnd)
    return <span dangerouslySetInnerHTML={{ __html: result }} />
  }

  return (
    <Box>
      {error ? (
        <Alert status="error" mb={4}>
          <AlertIcon />
          {error.message || 'שגיאה בטעינת ההסכתים'}
        </Alert>
      ) : isLoading ? (
        <Center>
          <Spinner />
        </Center>
      ) : podcasts.length === 0 ? (
        <Center>
          <Text>אין הסכתים</Text>
        </Center>
      ) : (
        <>
          <Table mb={4} size="sm">
            <Tbody>
              {podcasts.map((podcast) => (
                <Tr
                  key={podcast.id}
                  onClick={() => {
                    setSelectedPodcasts(prev =>
                      prev.includes(podcast.id)
                        ? prev.filter(id => id !== podcast.id)
                        : [...prev, podcast.id]
                    )
                  }}
                  cursor="pointer"
                  bg={selectedPodcasts.includes(podcast.id) ? 'blue.50' : undefined}
                >
                  <Td width="60px" padding={2}>
                    {podcast.image_url && (
                      <Image
                        src={podcast.image_url}
                        alt={podcast.title}
                        height="40px"
                        objectFit="contain"
                      />
                    )}
                  </Td>
                  <Td padding={2}>{podcast.title}</Td>
                  <Td padding={2} textAlign="left" width="120px">
                    {podcast.episode_count} פרקים
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          <ButtonGroup mb={4} width="100%" justifyContent="space-between">
            <Button colorScheme="blue" onClick={handleRefresh}>
              רענן
            </Button>
            <Button colorScheme="red" size="sm" onClick={handleEmpty}>
              רוקן
            </Button>
          </ButtonGroup>

          <Box mb={4}>
            <Input
              placeholder="חיפוש בכותרת ובתיאור..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              mb={4}
            />

            <Stack spacing={4}>
              <Flex gap={8}>
                <Box flex={1}>
                  <HStack spacing={4} align="center">
                    <Text whiteSpace="nowrap">משקל כותרת:</Text>
                    <Slider
                      value={titleWeight}
                      onChange={setTitleWeight}
                      min={0}
                      max={100}
                      flex={1}
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb />
                    </Slider>
                    <Text whiteSpace="nowrap">{titleWeight}%</Text>
                  </HStack>
                </Box>

                <Box flex={1}>
                  <HStack spacing={4} align="center">
                    <Text whiteSpace="nowrap">משקל תיאור:</Text>
                    <Slider
                      value={descriptionWeight}
                      onChange={setDescriptionWeight}
                      min={0}
                      max={100}
                      flex={1}
                    >
                      <SliderTrack>
                        <SliderFilledTrack />
                      </SliderTrack>
                      <SliderThumb />
                    </Slider>
                    <Text whiteSpace="nowrap">{descriptionWeight}%</Text>
                  </HStack>
                </Box>
              </Flex>
            </Stack>
          </Box>

          {isSearching ? (
            <Center>
              <Spinner />
            </Center>
          ) : searchResults.length > 0 ? (
            <Grid
              templateColumns="repeat(3, 1fr)"
              gap={4}
              sx={{
                '& > *:nth-of-type(3n+1)': { order: 3 },
                '& > *:nth-of-type(3n+2)': { order: 2 },
                '& > *:nth-of-type(3n+3)': { order: 1 },
              }}
            >
              {searchResults.map(({ episode, matches }) => (
                <Card key={episode.id}>
                  <CardBody>
                    <Flex gap={4}>
                      <Box flexShrink={0}>
                        <Image
                          src={episode.image_url || ''}
                          alt={episode.title}
                          height="72px"
                          width="72px"
                          objectFit="contain"
                          borderRadius="lg"
                        />
                      </Box>
                      <Stack spacing={2} flex={1} overflow="hidden">
                        <Heading size="md" wordBreak="break-word">
                          {highlightText(episode.title, matches?.title)}
                        </Heading>
                        <Text fontSize="sm" color="gray.600">
                          {new Date(episode.publish_date).toLocaleString('he-IL')}
                        </Text>
                        <Text wordBreak="break-word">
                          {highlightText(episode.description, matches?.description)}
                        </Text>
                        <ButtonGroup>
                          <Button
                            colorScheme="blue"
                            size="sm"
                            onClick={() => copyToClipboard(episode.url)}
                          >
                            העתק קישור
                          </Button>
                          <Button
                            as="a"
                            href={episode.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            size="sm"
                          >
                            נגן
                          </Button>
                        </ButtonGroup>
                      </Stack>
                    </Flex>
                  </CardBody>
                </Card>
              ))}
            </Grid>
          ) : searchQuery.trim() ? (
            <Center>
              <Text>לא נמצאו תוצאות</Text>
            </Center>
          ) : null}
        </>
      )}
    </Box>
  )
}